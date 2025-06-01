#!/bin/bash

# Smash Overlay Stop Script
# This script stops the running Smash Overlay application

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if the pid file exists
if [ -f .flask.pid ]; then
    PID=$(cat .flask.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping Smash Overlay (PID: $PID)..."
        kill $PID
        rm .flask.pid
        echo "Smash Overlay stopped successfully."
    else
        echo "Smash Overlay is not running with PID $PID."
        rm .flask.pid
    fi
else
    # Try to find and kill the process using pgrep
    PID=$(pgrep -f "flask run")
    if [ -n "$PID" ]; then
        echo "Stopping Smash Overlay (PID: $PID)..."
        kill $PID
        echo "Smash Overlay stopped successfully."
    else
        echo "Smash Overlay is not running."
    fi
fi
