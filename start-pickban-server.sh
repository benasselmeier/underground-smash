#!/bin/bash

# Pick/Ban Server Launcher Script
# This script makes it easy to start the Pick/Ban server

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

echo "🎯 Starting Underground Smash Pick/Ban Server..."
echo "📱 This server provides tablet interfaces for stage pick/ban"
echo ""

# Start the pick/ban server
echo "🔧 Running in single-process mode (debug/reloader disabled)"
FLASK_DEBUG=0 FLASK_ENV=production PICKBAN_DEBUG=0 python3 pickban-server.py
