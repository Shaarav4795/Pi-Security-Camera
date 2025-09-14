# Raspberry Pi Security Camera System

A smart continuous recording security camera that uses motion detection to preserve footage, captures photos, and uploads everything to Discord for free cloud storage.

## What It Does

- **Continuous Recording**: Records in 20-second segments automatically
- **Smart Preservation**: Only keeps segments with detected motion
- **Instant Photos**: Captures high-res photos when motion detected  
- **Pre/Post Context**: See what happened before, during, and after motion events
- **Discord Upload**: Automatically uploads to Discord via webhook
- **Auto Cleanup**: Deletes local files after successful upload
- **Beautiful Timestamps**: "Motion detected!\nTimestamp: 14th September 2025 at 3:05 pm"

## Prerequisites

- Raspberry Pi (tested on Pi 4) with camera module
- Raspberry Pi OS (Debian-based)
- Internet connection for Discord uploads
- Discord server for receiving alerts

## ⚡ Quick Setup

### Step 1: Install System Dependencies
```bash
sudo apt update
sudo apt install -y libcamera-dev python3-libcamera ffmpeg
```

### Step 2: Clone and Setup
```bash
git clone https://github.com/yourusername/Raspi-Security-Camera.git
cd Raspi-Security-Camera
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv env --system-site-packages
source env/bin/activate
pip install -r requirements.txt
```

### Step 4: Set Up Discord Webhook
1. Create a Discord server (or use existing one)
2. Create a channel for security alerts
3. Go to **Channel Settings** → **Integrations** → **Webhooks**
4. Click **Create Webhook** 
5. Copy the **Webhook URL**

### Step 5: Configure the System

Copy the configuration template and edit it:

```bash
cp config.py.example config.py
nano config.py
```

Replace the webhook URL:
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your/webhook/url/here"
```

### Step 6: Run the Security System
```bash
./run.sh
```

**That's it!** Your security camera is now continuously recording and monitoring for motion.

## How to Stop
Press **Ctrl+C** to stop the security system safely.

## Project Structure
```
Raspi-Security-Camera/
├── env/                         # Virtual environment 
├── config.py.example            # Configuration template
├── config.py                    # Configuration settings
├── motion_detector.py           # Continuous recording + motion detection
├── discord_webhook_notifier.py  # Discord upload handler
├── start_security_system.py     # Main system launcher
├── run.sh                       # Startup script
├── requirements.txt             # Python dependencies
├── video_cache/                 # Temporary video segments
├── photo_cache/                 # Temporary photos
├── .gitignore                   # Git ignore rules
└── README.md                    # This documentation
```

## How It Works

### Continuous Recording System
```
Timeline: [Segment A] [Segment B] [Segment C] [Segment D] 
Action:    DELETE      KEEP        DELETE      KEEP
Reason:    No motion   Motion!     No motion   Motion!
Result:    Discarded   → Discord   Discarded   → Discord
```

1. **Always Recording**: Camera continuously records 20-second H.264 segments
2. **Motion Analysis**: Each frame is analyzed for motion using computer vision
3. **Smart Decisions**: Segments with motion are converted to MP4 and kept
4. **Auto Cleanup**: Segments without motion are automatically deleted
5. **Discord Upload**: Photos and videos are uploaded with beautiful timestamps
6. **Storage Management**: Local files are deleted after successful upload

## Configuration Options

Edit `config.py` to customize:

```python
# Motion Detection
MOTION_THRESHOLD = 6          # Lower = more sensitive (1-15)
COOLDOWN_PERIOD = 30          # Seconds between motion detections

# Video Settings  
VIDEO_DURATION = 20           # Seconds per segment
VIDEO_RESOLUTION = (1280, 720) # Recording resolution
FRAME_RATE = 30               # FPS

# Paths
VIDEO_CACHE_DIR = "./video_cache"
PHOTO_CACHE_DIR = "./photo_cache"

# Discord
DISCORD_WEBHOOK_URL = "your_webhook_url_here"
```

## Troubleshooting

### Camera Issues
```bash
# Enable camera interface
sudo raspi-config
# → Interface Options → Camera → Enable

# Check camera detection
libcamera-hello --list-cameras
```

### Permission Issues
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Reboot after this change
sudo reboot
```

### Discord Upload Issues
- **File too large**: Discord limits are 8MB (normal) / 50MB (Nitro)
- **Invalid webhook**: Double-check your webhook URL in `config.py`
- **Network issues**: Check internet connection and Discord server status

### Motion Detection Issues
- **Too sensitive**: Increase `MOTION_THRESHOLD` in `config.py`
- **Not sensitive enough**: Decrease `MOTION_THRESHOLD` 
- **False triggers**: Adjust camera position to avoid moving shadows/leaves

## Running on Startup (Auto-Start)

To automatically start on boot:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
@reboot sleep 30 && cd /home/pi/Raspi-Security-Camera && ./run.sh
```

Or create a systemd service for more robust startup control.

## Performance & Storage

### System Requirements
- **CPU**: ~15-25% on Pi 4 during recording
- **RAM**: ~150-200MB
- **Storage**: Only segments with motion are kept
- **Network**: ~4MB per 20-second video upload

### File Sizes
- **Photos**: ~150-200KB each (JPEG)
- **Videos**: ~4-6MB per 20-second segment (H.264→MP4)
- **Continuous recording**: No permanent storage impact (auto-cleanup)

## Security & Privacy

- **Local Processing**: All motion detection happens on-device
- **Secure Webhooks**: Discord webhooks use HTTPS encryption
- **Private Storage**: Your Discord server = your private cloud
- **No Third Parties**: No external services beyond Discord
- **Webhook Security**: Keep your webhook URL private

## Advanced Usage

### Custom Motion Zones
Edit `motion_detector.py` to define specific areas for motion detection.

### Multiple Cameras  
Run multiple instances with different camera indices and Discord channels.

### Integration Options (feel free to create a pull request for these!)
- Home Assistant integration via webhooks
- SMS alerts via Twilio
- Email notifications via SMTP


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## Need Help?

- Check the troubleshooting section above
- Review the configuration options
- Test your camera with `libcamera-hello`
- Verify your Discord webhook URL

Happy monitoring!
