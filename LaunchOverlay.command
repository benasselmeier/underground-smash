#!/bin/bash
# Launcher script for Underground Smash Overlay

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the start script
bash start-smash-overlay.sh

# Keep the terminal window open until the user presses a key
echo ""
echo "Press any key to close this window..."
read -n 1 -s
