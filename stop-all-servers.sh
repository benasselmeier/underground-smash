#!/bin/bash

# Stop All Servers Script

echo "🛑 Stopping Underground Smash Servers..."

# Stop by process name
pkill -f "python.*app\.py"
pkill -f "pickban-server\.py"

# Also stop by saved PIDs if available
if [ -f "server_pids.txt" ]; then
    echo "📝 Stopping servers by saved PIDs..."
    while read line; do
        PID=$(echo $line | grep -o '[0-9]*')
        if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "   Stopped PID: $PID"
        fi
    done < server_pids.txt
    rm server_pids.txt
fi

echo "✅ All servers stopped"
