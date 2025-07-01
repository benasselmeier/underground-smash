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
    echo "You can access it at:"
    echo "- http://127.0.0.1:5000"
    IP=$(ipconfig getifaddr en0)
    echo "- http://$IP:5000"
else
    # Start the Flask application
    echo "Starting Smash Overlay..."
    echo "The application can be accessed at:"
    echo "- http://127.0.0.1:5000"
    IP=$(ipconfig getifaddr en0)
    echo "- http://$IP:5000"
    
    # Run Flask in the background with host set to 0.0.0.0 to allow external access
    FLASK_RUN_HOST=0.0.0.0 python -m flask run &
    
    # Store the process ID
    echo $! > .flask.pid
    
    # Print message about accessing the application
    echo ""
    echo "You can access the application by manually opening one of these URLs in your browser:"
    echo "- http://127.0.0.1:5000"
    echo "- http://$IP:5000"
    echo ""
fi
