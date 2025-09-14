import os
import time
import requests
from datetime import datetime
import config

def format_timestamp(filename):
    """Convert filename timestamp to formatted string"""
    try:
        # Extract timestamp from filename (format: 2025-09-14_15-05-51)
        timestamp_part = filename.split('.')[0]  # Remove extension
        date_part, time_part = timestamp_part.split('_')
        
        # Parse the datetime
        dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H-%M-%S")
        
        # Format as "14th September 2025 at 3:05 pm"
        day = dt.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        month = dt.strftime("%B")
        year = dt.year
        time_str = dt.strftime("%I:%M %p").lower()
        
        return f"{day}{suffix} {month} {year} at {time_str}"
    except Exception as e:
        # Fallback to original format if parsing fails
        return filename.replace('_', ' ').replace('.jpg', '').replace('.mp4', '')

def send_to_discord_webhook(webhook_url, file_path, message="Motion detected!"):
    """Send file to Discord channel via webhook"""
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'content': message}
            
            response = requests.post(webhook_url, data=data, files=files)
            
            if response.status_code == 200:
                print(f"Successfully sent {os.path.basename(file_path)} to Discord")
                return True
            else:
                print(f"Failed to send {os.path.basename(file_path)}: {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"Error sending file to Discord: {e}")
        return False

def process_files_webhook():
    """Process and send files using Discord webhook"""
    webhook_url = config.DISCORD_WEBHOOK_URL
    
    if webhook_url == "YOUR_WEBHOOK_URL_HERE":
        print("Please configure DISCORD_WEBHOOK_URL in config.py")
        return
    
    # Process photos
    if os.path.exists(config.PHOTO_CACHE_DIR):
        photo_files = [f for f in os.listdir(config.PHOTO_CACHE_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
        for photo_file in photo_files:
            photo_path = os.path.join(config.PHOTO_CACHE_DIR, photo_file)
            formatted_timestamp = format_timestamp(photo_file)
            message = f"📸 Motion detected!\nTimestamp: {formatted_timestamp}"
            
            if send_to_discord_webhook(webhook_url, photo_path, message):
                os.remove(photo_path)  # Delete after successful upload
                print(f"Deleted local photo: {photo_file}")
    
    # Process videos
    if os.path.exists(config.VIDEO_CACHE_DIR):
        video_files = [f for f in os.listdir(config.VIDEO_CACHE_DIR) if f.endswith(('.mp4', '.avi', '.mov'))]
        for video_file in video_files:
            video_path = os.path.join(config.VIDEO_CACHE_DIR, video_file)
            formatted_timestamp = format_timestamp(video_file)
            message = f"🎥 Motion detected!\nTimestamp: {formatted_timestamp}"
            
            if send_to_discord_webhook(webhook_url, video_path, message):
                os.remove(video_path)  # Delete after successful upload
                print(f"Deleted local video: {video_file}")

def main():
    """Main loop for webhook notifier"""
    print("Discord Webhook Notifier started")
    print("Checking for new files every 60 seconds...")
    
    while True:
        try:
            process_files_webhook()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nShutting down webhook notifier...")
            break
        except Exception as e:
            print(f"Error in webhook notifier: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()
