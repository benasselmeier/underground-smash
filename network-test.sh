#!/bin/bash

# Comprehensive Network Connectivity Tester
# This script helps diagnose why tablets can't connect to the servers

echo "🔍 Advanced Network Connectivity Diagnostics"
echo "=============================================="
echo ""

# Get network interface information
echo "📡 Network Interface Information:"
LOCAL_IP_EN0=$(ipconfig getifaddr en0 2>/dev/null)
LOCAL_IP_EN1=$(ipconfig getifaddr en1 2>/dev/null)

if [ ! -z "$LOCAL_IP_EN0" ]; then
    echo "   WiFi (en0): $LOCAL_IP_EN0"
    ACTIVE_IP=$LOCAL_IP_EN0
    ACTIVE_INTERFACE="en0"
elif [ ! -z "$LOCAL_IP_EN1" ]; then
    echo "   Ethernet (en1): $LOCAL_IP_EN1"
    ACTIVE_IP=$LOCAL_IP_EN1
    ACTIVE_INTERFACE="en1"
else
    echo "   ❌ No active network interface found"
    exit 1
fi

echo ""

# Test server ports
echo "🚀 Testing Server Accessibility:"
test_port() {
    local port=$1
    local service=$2
    
    echo -n "   Testing $service (port $port)... "
    
    if curl -s --connect-timeout 3 "http://localhost:$port" >/dev/null 2>&1; then
        echo "✅ Locally accessible"
    else
        echo "❌ Not accessible locally"
        return 1
    fi
    
    echo -n "   Testing $service via IP ($ACTIVE_IP:$port)... "
    if curl -s --connect-timeout 3 "http://$ACTIVE_IP:$port" >/dev/null 2>&1; then
        echo "✅ Accessible via IP"
    else
        echo "❌ Not accessible via IP"
        return 1
    fi
}

test_port 3000 "Main Overlay Server"
test_port 5002 "Pick/Ban Server"

echo ""

# Check firewall settings
echo "🔥 Firewall Analysis:"
if command -v pfctl >/dev/null 2>&1; then
    if sudo pfctl -s info 2>/dev/null | grep -q "Status: Enabled"; then
        echo "   ⚠️  Packet Filter (pfctl) is enabled"
        echo "   This might block incoming connections"
    else
        echo "   ✅ Packet Filter appears disabled"
    fi
fi

# Check application firewall
if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -q "enabled"; then
    echo "   ⚠️  Application Firewall is enabled"
    echo "   Python may need to be allowed through the firewall"
else
    echo "   ✅ Application Firewall is disabled"
fi

echo ""

# Check network routing
echo "🌐 Network Routing:"
DEFAULT_ROUTE=$(route -n get default 2>/dev/null | grep gateway | awk '{print $2}')
if [ ! -z "$DEFAULT_ROUTE" ]; then
    echo "   Default Gateway: $DEFAULT_ROUTE"
    
    # Check if we can ping the gateway
    if ping -c 1 -W 2000 "$DEFAULT_ROUTE" >/dev/null 2>&1; then
        echo "   ✅ Can reach default gateway"
    else
        echo "   ❌ Cannot reach default gateway"
    fi
else
    echo "   ❌ No default gateway found"
fi

echo ""

# Generate QR codes for easy tablet access
echo "📱 Tablet Access URLs:"
echo "   Main Server: http://$ACTIVE_IP:3000"
echo "   Mobile Panel: http://$ACTIVE_IP:3000/mobile"
echo "   Pick/Ban Player 1: http://$ACTIVE_IP:5002/player/1"
echo "   Pick/Ban Player 2: http://$ACTIVE_IP:5002/player/2"
echo ""

# Create simple test server to verify connectivity
echo "🧪 Starting Simple Test Server on Port 8888..."
echo "   This will help test basic connectivity"
echo ""

# Kill any existing test server
pkill -f "python.*8888" 2>/dev/null

# Start test server in background
python3 -c "
import http.server
import socketserver
import threading

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
<!DOCTYPE html>
<html>
<head><title>Network Test</title></head>
<body style=\"font-family: Arial; text-align: center; padding: 50px;\">
<h1>🎉 SUCCESS!</h1>
<h2>Your tablet can reach this Mac!</h2>
<p>IP: $ACTIVE_IP</p>
<p>Time: $(date)</p>
<p style=\"color: green; font-size: 20px;\">Network connectivity is working!</p>
</body>
</html>
        '''.replace(b'\$ACTIVE_IP', b'$ACTIVE_IP'))

with socketserver.TCPServer(('0.0.0.0', 8888), MyHandler) as httpd:
    print('Test server started on port 8888')
    httpd.serve_forever()
" &

TEST_SERVER_PID=$!

echo "✅ Test server started (PID: $TEST_SERVER_PID)"
echo ""
echo "🔍 TROUBLESHOOTING STEPS:"
echo ""
echo "1. 📱 Test basic connectivity first:"
echo "   Open this URL on your tablet: http://$ACTIVE_IP:8888"
echo "   If this works, the network is fine and the issue is with the main servers"
echo ""
echo "2. 🔧 If step 1 fails, try these solutions:"
echo "   a) Make sure tablet is on the same WiFi network as this Mac"
echo "   b) Restart your WiFi router"
echo "   c) Disable 'Private WiFi Address' on your tablet"
echo "   d) Try using a different device (another phone/tablet)"
echo ""
echo "3. 🍎 macOS-specific fixes:"
echo "   a) System Preferences → Security & Privacy → Firewall → Turn Off"
echo "   b) System Preferences → Sharing → Enable 'Internet Sharing' temporarily"
echo "   c) Restart network services: sudo dscacheutil -flushcache"
echo ""
echo "4. 🌐 Advanced network fixes:"
echo "   a) Reset network settings on your tablet"
echo "   b) Try connecting tablet via hotspot from another device"
echo "   c) Check router settings for AP isolation (should be disabled)"
echo ""

echo "Press Ctrl+C when done testing, then run this script again to stop the test server"
echo ""

# Wait for user to stop
trap "echo '🛑 Stopping test server...'; kill $TEST_SERVER_PID 2>/dev/null; exit 0" INT

wait
