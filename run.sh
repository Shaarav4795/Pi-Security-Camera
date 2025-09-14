#!/bin/bash
# Simple script to activate virtual environment and start the security system

cd "$(dirname "$0")"
echo "Starting Raspberry Pi Security Camera System..."
source env/bin/activate
python3 start_security_system.py
