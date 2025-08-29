#!/bin/bash

# Smash Overlay Stop Script (Port 80 Version)
# This script stops the running Smash Overlay application on port 80

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if the pid file exists
if [ -f .flask80.pid ]; then
    PID=$(cat .flask80.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping Smash Overlay on port 80 (PID: $PID)..."
        kill $PID
        rm .flask80.pid
        echo "✅ Smash Overlay stopped successfully."
    else
        echo "⚠️  Smash Overlay is not running with PID $PID."
        rm .flask80.pid
    fi
else
    # Try to find and kill the process using lsof
    PIDS=$(lsof -ti :80 2>/dev/null)
    if [ -n "$PIDS" ]; then
        for PID in $PIDS; do
            # Check if it's a Python/Flask process
            if ps -p $PID -o command= | grep -q -E "(python|flask)"; then
                echo "Stopping Smash Overlay on port 80 (PID: $PID)..."
                kill $PID
                echo "✅ Smash Overlay stopped successfully."
                exit 0
            fi
        done
        echo "ℹ️  Found processes on port 80, but none are Python/Flask processes."
    else
        echo "ℹ️  Smash Overlay is not running on port 80."
    fi
fi
