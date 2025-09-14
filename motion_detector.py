import time
import os
from subprocess import call
from datetime import datetime
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
import threading
from libcamera import controls
import config

class ContinuousRecorder:
    def __init__(self, picam2):
        self.picam2 = picam2
        self.current_segment_path = None
        self.current_segment_start = None
        self.motion_detected_in_segment = False
        self.encoder = H264Encoder(bitrate=config.VIDEO_BITRATE, repeat=True)
        self.output = CircularOutput()
        self.segment_lock = threading.Lock()
        self.recording = False
        
    def start_new_segment(self):
        """Start recording a new 20-second segment"""
        with self.segment_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.current_segment_path = os.path.join(config.VIDEO_CACHE_DIR, f"{timestamp}.h264")
            self.current_segment_start = time.time()
            self.motion_detected_in_segment = False
            
            # Stop current encoder if running
            if self.recording:
                try:
                    self.picam2.stop_encoder()
                    self.recording = False
                except:
                    pass
            
            # Start new segment
            self.output.fileoutput = self.current_segment_path
            self.output.start()
            self.picam2.start_encoder(self.encoder, self.output)
            self.recording = True
            print(f"Started new segment: {os.path.basename(self.current_segment_path)}")
    
    def mark_motion_detected(self):
        """Mark that motion was detected in the current segment"""
        with self.segment_lock:
            self.motion_detected_in_segment = True
            print(f"Motion marked for segment: {os.path.basename(self.current_segment_path) if self.current_segment_path else 'None'}")
    
    def should_end_segment(self):
        """Check if current segment should end (after 20 seconds)"""
        if self.current_segment_start is None:
            return True
        return time.time() - self.current_segment_start >= config.VIDEO_DURATION
    
    def end_current_segment(self):
        """End current segment and decide whether to keep or delete it"""
        with self.segment_lock:
            if self.current_segment_path is None or not self.recording:
                return
            
            # Stop encoder and output
            try:
                self.picam2.stop_encoder()
                self.output.stop()
                self.recording = False
            except:
                pass
            
            time.sleep(0.5)  # Brief pause to ensure file is written
            
            if self.motion_detected_in_segment:
                # Keep the segment - convert to MP4
                self.convert_segment_to_mp4()
                print(f"Kept segment with motion: {os.path.basename(self.current_segment_path)}")
            else:
                # Delete the segment - no motion detected
                try:
                    if os.path.exists(self.current_segment_path):
                        os.remove(self.current_segment_path)
                        print(f"Deleted segment (no motion): {os.path.basename(self.current_segment_path)}")
                except Exception as e:
                    print(f"Error deleting segment: {e}")
            
            self.current_segment_path = None
            self.current_segment_start = None
            self.motion_detected_in_segment = False
    
    def convert_segment_to_mp4(self):
        """Convert H264 segment to MP4"""
        try:
            input_file = self.current_segment_path
            output_file = input_file.replace('.h264', '.mp4')
            command = f"ffmpeg -y -i {input_file} -c copy -movflags +faststart {output_file} 2>/dev/null"
            call(command, shell=True)
            os.remove(input_file)  # Remove h264 file
            print(f"Converted segment to MP4: {os.path.basename(output_file)}")
        except Exception as e:
            print(f"Error converting segment: {e}")
    
    def cleanup(self):
        """Cleanup when shutting down"""
        if self.recording:
            try:
                self.picam2.stop_encoder()
                self.output.stop()
            except:
                pass

def capture_photo(picam2, filename):
    """Capture a high-resolution photo"""
    photo_path = os.path.join(config.PHOTO_CACHE_DIR, f"{filename}.jpg")
    print(f"Capturing photo: {photo_path}")
    
    # Capture high-res image
    picam2.capture_file(photo_path)
    print(f"Photo captured: {photo_path}")
    return photo_path

def main():
    time_format = "%Y-%m-%d_%H-%M-%S"
    
    # Initialize camera
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(
        main={"size": config.VIDEO_RESOLUTION, "format": "RGB888"},
        lores={"size": config.LORES_RESOLUTION, "format": "YUV420"}
    )
    picam2.configure(video_config)
    picam2.set_controls({"FrameRate": config.FRAME_RATE})
    
    # Initialize continuous recorder
    recorder = ContinuousRecorder(picam2)
    
    picam2.start()
    
    # Start first segment
    recorder.start_new_segment()
    
    w, h = config.LORES_RESOLUTION
    prev = None
    last_motion_time = 0
    
    print("Continuous recording with motion detection started...")
    print(f"Recording in {config.VIDEO_DURATION}-second segments")
    
    try:
        while True:
            # Check if we need to start a new segment
            if recorder.should_end_segment():
                recorder.end_current_segment()
                recorder.start_new_segment()
            
            cur = picam2.capture_buffer("lores")
            cur = cur[:w * h].reshape(h, w)
            
            if prev is not None:
                mse = np.square(np.subtract(cur, prev)).mean()
                current_time = time.time()
                
                if mse > config.MOTION_THRESHOLD:
                    # Check cooldown period
                    if current_time - last_motion_time > config.COOLDOWN_PERIOD:
                        print("Motion detected!")
                        
                        # Mark current segment as having motion
                        recorder.mark_motion_detected()
                        
                        # Capture photo
                        try:
                            filename = datetime.now().strftime(time_format)
                            capture_photo(picam2, filename)
                        except Exception as e:
                            print(f"Error capturing photo: {e}")
                        
                        last_motion_time = current_time
            
            prev = cur
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print("\nShutting down motion detection...")
    finally:
        recorder.cleanup()
        recorder.end_current_segment()
        picam2.stop()
        print("Motion detection stopped")

if __name__ == "__main__":
    main()
