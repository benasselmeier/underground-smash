#!/bin/bash

# Stop Pick/Ban Server Script

echo "🛑 Stopping Underground Smash Pick/Ban Server..."

# Find and kill the pick/ban server process
PID=$(ps aux | grep '[p]ickban-server.py' | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "📱 Found Pick/Ban server running with PID: $PID"
    kill $PID
    sleep 2
    
    # Check if process is still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Process still running, forcing termination..."
        kill -9 $PID
    fi
    
    echo "✅ Pick/Ban server stopped successfully"
else
    echo "❌ No Pick/Ban server process found running"
fi

echo "🎯 Pick/Ban server shutdown complete"
