#!/bin/bash

# Start Both Servers Script
# Starts both the main overlay and pick/ban servers on working ports

echo "🚀 Starting Underground Smash Complete Setup..."
echo "=============================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "192.168.0.189")

echo "🌐 Local IP Address: $LOCAL_IP"
echo ""

# Kill any existing servers
echo "🧹 Cleaning up any existing servers..."
pkill -f "python.*app\.py" 2>/dev/null || true
pkill -f "python.*pickban-server\.py" 2>/dev/null || true
sleep 2

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
else
    source env/bin/activate
fi

echo ""
echo "🎮 Starting Main Overlay Server (Port 3000)..."
FLASK_RUN_PORT=3000 python3 app.py > /dev/null 2>&1 &
MAIN_PID=$!

sleep 3

echo "🎯 Starting Pick/Ban Server (Port 5002)..."
python3 pickban-server.py > /dev/null 2>&1 &
PICKBAN_PID=$!

sleep 3

echo ""
echo "✅ Both servers started successfully!"
echo ""
echo "📱 TABLET URLS - Use these on your tablets:"
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ 🎮 Player 1 Pick/Ban: http://$LOCAL_IP:5002/player/1    │"
echo "│ 🎮 Player 2 Pick/Ban: http://$LOCAL_IP:5002/player/2    │"
echo "│ 📱 Mobile Control:    http://$LOCAL_IP:3000/mobile       │"
echo "│ ⚙️  Admin Panel:      http://$LOCAL_IP:5002/admin        │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
echo "🖥️  DESKTOP URLS:"
echo "   📍 Main Control: http://$LOCAL_IP:3000"
echo "   📋 Pick/Ban Hub: http://$LOCAL_IP:5002"
echo ""
echo "🔧 To stop servers: ./stop-all-servers.sh"
echo ""
echo "📋 Process IDs:"
echo "   Main Server: $MAIN_PID"
echo "   Pick/Ban Server: $PICKBAN_PID"
echo ""

# Save PIDs for stop script
echo "$MAIN_PID" > .main_server.pid
echo "$PICKBAN_PID" > .pickban_server.pid

echo "🎉 Setup complete! Test the URLs above on your tablets."
