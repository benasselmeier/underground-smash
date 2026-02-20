#!/bin/bash

# Quick Network Fixes Script
# This script applies common fixes for Mac network connectivity issues

echo "🔧 Applying Common Network Fixes..."
echo "===================================="
echo ""

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo "🌐 Current IP: $LOCAL_IP"
echo ""

# Function to check if user wants to proceed
confirm() {
    read -p "$1 (y/N): " response
    case $response in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 1. Flush DNS cache
echo "1. 🧹 Flushing DNS cache..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
echo "   ✅ DNS cache flushed"
echo ""

# 2. Check and offer to disable firewall
echo "2. 🔥 Checking firewall status..."
if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    echo "   ⚠️  Application firewall is enabled"
    if confirm "   Disable application firewall temporarily?"; then
        sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
        echo "   ✅ Application firewall disabled"
    fi
else
    echo "   ✅ Application firewall already disabled"
fi
echo ""

# 3. Check for AirPlay receiver conflicts
echo "3. 📺 Checking AirPlay receiver..."
if lsof -i :5000 >/dev/null 2>&1; then
    echo "   ⚠️  Port 5000 is in use (likely AirPlay)"
    echo "   💡 Tip: Disable AirPlay Receiver in System Preferences → General → AirDrop & Handoff"
else
    echo "   ✅ Port 5000 is available"
fi
echo ""

# 4. Restart network interface
echo "4. 🔄 Network interface reset..."
if confirm "Restart network interface? This will briefly disconnect WiFi"; then
    sudo ifconfig en0 down
    sleep 2
    sudo ifconfig en0 up
    echo "   ✅ Network interface restarted"
    
    # Wait for IP to come back
    echo "   ⏳ Waiting for IP address..."
    for i in {1..10}; do
        NEW_IP=$(ipconfig getifaddr en0 2>/dev/null)
        if [ ! -z "$NEW_IP" ]; then
            echo "   ✅ New IP: $NEW_IP"
            LOCAL_IP=$NEW_IP
            break
        fi
        sleep 1
    done
else
    echo "   ⏭️  Skipped network restart"
fi
echo ""

# 5. Test server accessibility
echo "5. 🧪 Testing server accessibility..."
if curl -s --connect-timeout 3 "http://localhost:3000" >/dev/null 2>&1; then
    echo "   ✅ Main server (port 3000) is accessible locally"
else
    echo "   ❌ Main server (port 3000) is not accessible"
fi

if curl -s --connect-timeout 3 "http://localhost:5002" >/dev/null 2>&1; then
    echo "   ✅ Pick/ban server (port 5002) is accessible locally"
else
    echo "   ❌ Pick/ban server (port 5002) is not accessible"
fi
echo ""

# 6. Generate updated URLs
echo "6. 📱 Updated tablet URLs:"
echo "   Main Server: http://$LOCAL_IP:3000"
echo "   Mobile Panel: http://$LOCAL_IP:3000/mobile" 
echo "   Pick/Ban Player 1: http://$LOCAL_IP:5002/player/1"
echo "   Pick/Ban Player 2: http://$LOCAL_IP:5002/player/2"
echo ""

# 7. Additional troubleshooting tips
echo "7. 💡 Additional tips if tablets still can't connect:"
echo ""
echo "   📱 Tablet Settings:"
echo "   • Make sure tablet is on the same WiFi network"
echo "   • Disable 'Private WiFi Address' in WiFi settings"
echo "   • Try forgetting and reconnecting to the WiFi network"
echo "   • Clear browser cache on tablet"
echo ""
echo "   🏠 Router Settings:"
echo "   • Disable 'AP Isolation' or 'Client Isolation'"
echo "   • Enable 'Multicast' or 'IGMP Snooping'"
echo "   • Restart the router"
echo ""
echo "   🍎 Mac Settings:"
echo "   • System Preferences → Sharing → Disable 'Internet Sharing'"
echo "   • System Preferences → Network → Advanced → TCP/IP → Renew DHCP Lease"
echo ""

echo "🔧 Network fixes complete!"
echo ""
echo "Next step: Run './network-test.sh' to test connectivity"
