#!/bin/bash

# Smash Overlay Launcher Script (Port 80 Version)
# This script starts the overlay on port 80 for cleaner URLs (requires sudo)

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "🔐 This script needs administrator privileges to use port 80"
    echo "💡 This allows cleaner URLs: mbsmash.local instead of mbsmash.local:5000"
    echo ""
    echo "Re-running with sudo..."
    sudo bash "$0" "$@"
    exit $?
fi

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

# Check if the app is already running on port 80
if lsof -i :80 | grep -q python; then
    echo "Smash Overlay is already running on port 80!"
    echo ""
    IP=$(ipconfig getifaddr en0)
    echo "🖥️  Desktop Control Panel:"
    echo "- http://mbsmash.local"
    echo "- http://$IP"
    echo ""
    echo "📱 Mobile Control Panel:"
    echo "- http://mbsmash.local/mobile"
    echo "- http://$IP/mobile"
    echo ""
else
    # Start the Flask application on port 80
    echo "Starting Smash Overlay on port 80..."
    echo ""
    IP=$(ipconfig getifaddr en0)
    echo "🖥️  DESKTOP CONTROL PANEL:"
    echo "- http://mbsmash.local"
    echo "- http://$IP"
    echo ""
    echo "📱 MOBILE CONTROL PANEL:"
    echo "- http://mbsmash.local/mobile"
    echo "- http://$IP/mobile"
    echo ""
    
    # Run Flask on port 80
    FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=80 python -m flask run &
    
    # Store the process ID
    echo $! > .flask80.pid
    
    echo "🎮 Smash Overlay is now running on port 80!"
    echo ""
    echo "✨ Clean URLs available:"
    echo "🖥️  Desktop: http://mbsmash.local"
    echo "📱 Mobile: http://mbsmash.local/mobile"
    echo ""
    echo "💡 Bookmark 'http://mbsmash.local/mobile' on your phone!"
    echo ""
fi
