#!/bin/bash

# Post-Restart Quick Setup Script
# Run this after restarting your Mac to get both servers running

echo "🚀 Post-Restart Underground Smash Setup"
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "🌐 Your local IP: $LOCAL_IP"
echo ""

# Activate virtual environment
if [ -d "env" ]; then
    source env/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found - run setup first"
    exit 1
fi

echo ""
echo "🎮 Starting Main Overlay Server on port 3000..."
export FLASK_RUN_PORT=3000
nohup python3 app.py > overlay_server.log 2>&1 &
OVERLAY_PID=$!
echo "   PID: $OVERLAY_PID"

sleep 3

echo ""
echo "🎯 Starting Pick/Ban Server on port 5002..."
nohup python3 pickban-server.py > pickban_server.log 2>&1 &
PICKBAN_PID=$!
echo "   PID: $PICKBAN_PID"

sleep 3

echo ""
echo "🔍 Checking if servers started successfully..."
if ps -p $OVERLAY_PID > /dev/null; then
    echo "✅ Main Overlay Server: RUNNING"
else
    echo "❌ Main Overlay Server: FAILED"
fi

if ps -p $PICKBAN_PID > /dev/null; then
    echo "✅ Pick/Ban Server: RUNNING"
else
    echo "❌ Pick/Ban Server: FAILED"
fi

echo ""
echo "📱 URLs for your tablet:"
echo "========================================"
echo "🎮 Main Mobile Control:"
echo "   http://$LOCAL_IP:3000/mobile"
echo ""
echo "🎯 Pick/Ban Player 1:"
echo "   http://$LOCAL_IP:5002/player/1"
echo ""
echo "🎯 Pick/Ban Player 2:"
echo "   http://$LOCAL_IP:5002/player/2"
echo ""
echo "⚙️  Pick/Ban Admin:"
echo "   http://$LOCAL_IP:5002/admin"
echo ""

echo "📋 Quick Test Steps:"
echo "1. Try opening http://$LOCAL_IP:3000/mobile on your tablet"
echo "2. If that works, try http://$LOCAL_IP:5002/player/1"
echo "3. Make sure your tablet is on the same WiFi network"
echo ""

echo "📝 Process IDs saved to stop later:"
echo "Main Server PID: $OVERLAY_PID" > server_pids.txt
echo "Pick/Ban PID: $PICKBAN_PID" >> server_pids.txt

echo "💡 To stop servers later: ./stop-all-servers.sh"
