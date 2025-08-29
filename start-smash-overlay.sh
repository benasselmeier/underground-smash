#!/bin/bash

# Smash Overlay Launcher Script
# This script makes it easy to start the Smash Overlay application

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

# Check if the app is already running
if pgrep -f "flask run" > /dev/null; then
    echo "Smash Overlay is already running!"
    echo ""
    echo "Desktop Control Panel:"
    echo "- http://127.0.0.1:5000"
    IP=$(ipconfig getifaddr en0)
    echo "- http://$IP:5000"
    echo "- http://mbsmash.local:5000"
    echo ""
    echo "📱 Mobile Control Panel:"
    echo "- http://$IP:5000/mobile"
    echo "- http://mbsmash.local:5000/mobile"
    echo ""
else
    # Start the Flask application
    echo "Starting Smash Overlay..."
    echo "The application can be accessed at:"
    echo "- Desktop Control Panel: http://127.0.0.1:5000"
    IP=$(ipconfig getifaddr en0)
    echo "- Desktop Control Panel: http://$IP:5000"
    echo "- Desktop Control Panel: http://mbsmash.local:5000"
    echo ""
    echo "📱 MOBILE CONTROL PANEL:"
    echo "- On your phone/tablet: http://$IP:5000/mobile"
    echo "- On your phone/tablet: http://mbsmash.local:5000/mobile"
    echo "- Make sure your mobile device is on the same WiFi network"
    echo ""
    
    # Run Flask in the background with host set to 0.0.0.0 to allow external access
    FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5000 python -m flask run &
    
    # Store the process ID
    echo $! > .flask.pid
    
    # Print message about accessing the application
    echo "🎮 Smash Overlay is now running!"
    echo ""
    echo "Desktop Control Panel:"
    echo "- http://127.0.0.1:5000"
    echo "- http://$IP:5000"
    echo "- http://mbsmash.local:5000"
    echo ""
    echo "📱 Mobile Control Panel:"
    echo "- http://$IP:5000/mobile"
    echo "- http://mbsmash.local:5000/mobile"
    echo "  (Access these URLs from your phone/tablet browser)"
    echo ""
fi
