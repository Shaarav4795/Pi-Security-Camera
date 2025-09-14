#!/usr/bin/env python3
"""
Raspberry Pi Security Camera System Startup Script
Runs both motion detection and Discord webhook notification
"""

import subprocess
import signal
import sys
import time

processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down security system...")
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
    
    # Wait for processes to terminate
    time.sleep(2)
    
    # Force kill if still running
    for process in processes:
        if process.poll() is None:
            process.kill()
    
    print("Security system stopped")
    sys.exit(0)

def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Raspberry Pi Security Camera System")
    print("=" * 50)
    
    # Start motion detection
    print("Starting motion detection...")
    motion_process = subprocess.Popen([sys.executable, "motion_detector.py"])
    processes.append(motion_process)
    
    # Start Discord webhook notifier
    print("Starting Discord webhook notifier...")
    notifier_process = subprocess.Popen([sys.executable, "discord_webhook_notifier.py"])
    processes.append(notifier_process)
    
    print("Security system is running!")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Keep the main process running
    try:
        while True:
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"Process {i} has died with return code {process.returncode}")
                    # Could restart the process here if desired
            
            time.sleep(5)  # Check every 5 seconds
    
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
