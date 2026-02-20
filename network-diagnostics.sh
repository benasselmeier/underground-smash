#!/bin/bash

# Network Troubleshooting Script for Underground Smash Overlay
# This script helps diagnose and fix network accessibility issues

echo "🔍 Underground Smash Overlay - Network Diagnostics"
echo "=================================================="
echo ""

# Get local IP address
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "Unable to detect")
echo "🌐 Local IP Address: $LOCAL_IP"
echo ""

# Check if common ports are in use
echo "🔍 Checking port availability..."
echo ""

check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "❌ Port $port ($service): IN USE"
        echo "   Process using port:"
        lsof -i :$port | head -2
        echo ""
    else
        echo "✅ Port $port ($service): AVAILABLE"
    fi
}

check_port 5000 "Main Overlay Server"
check_port 5001 "Pick/Ban Server" 
check_port 8080 "Alternative Port"
check_port 3000 "Alternative Port"

echo ""
echo "🔥 macOS Firewall Status:"
if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    echo "⚠️  Firewall is ENABLED - this may block network access"
    echo "   To allow Python through firewall:"
    echo "   System Preferences → Security & Privacy → Firewall → Firewall Options"
    echo "   Add Python to the allowed applications list"
else
    echo "✅ Firewall is disabled or allows all connections"
fi

echo ""
echo "🍎 AirPlay Receiver Check (uses port 5000):"
if pgrep -f "AirPlayXPCHelper\|rapportd" >/dev/null; then
    echo "⚠️  AirPlay Receiver appears to be running (may use port 5000)"
    echo "   To disable: System Preferences → General → AirDrop & Handoff"
    echo "   Turn off 'AirPlay Receiver'"
else
    echo "✅ AirPlay Receiver doesn't appear to be blocking port 5000"
fi

echo ""
echo "📱 Testing Network Connectivity:"
echo "   Run this from your tablet browser to test connectivity:"
echo "   http://$LOCAL_IP:8080"
echo ""

echo "🚀 Recommended Actions:"
echo "1. Start main server on port 8080: ./start-smash-overlay-alt.sh"
echo "2. Start pick/ban server on port 5001: ./start-pickban-server.sh"
echo "3. Test from tablet: http://$LOCAL_IP:8080/mobile"
echo "4. Test pick/ban: http://$LOCAL_IP:5001/player/1"
echo ""

echo "🔧 If tablets still can't connect:"
echo "1. Check that devices are on the same WiFi network"
echo "2. Disable macOS firewall temporarily to test"
echo "3. Try alternative ports (3000, 8080, 9000)"
echo "4. Restart your router if needed"
echo ""

read -p "Press Enter to continue..."
