#!/bin/bash

# Alternative Smash Overlay Launcher Script (Port 8080)
# This script starts the overlay on port 8080 to avoid conflicts with AirPlay

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "Setting up virtual environment for the first time..."
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
else
    # Activate the virtual environment
    source env/bin/activate
fi

# Check if requirements need updating
pip install -r requirements.txt --quiet

echo "🎮 Starting Underground Smash Overlay on Port 8080..."
echo "📱 This avoids conflicts with macOS AirPlay Receiver"
echo ""

# Get local IP for display
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "🌐 Access URLs:"
echo "   📍 Desktop: http://$LOCAL_IP:8080"
echo "   📱 Mobile: http://$LOCAL_IP:8080/mobile"
echo "   🎯 mDNS: http://mbsmash.local:8080 (if working)"
echo ""

# Set environment variable for port and start
export FLASK_RUN_PORT=8080
python3 app.py
