# 🎯 Underground Smash - Pick/Ban Server Setup Complete!

## 🌐 Server Status: RUNNING ✅

Both servers are now running and accessible from tablets on your network!

### 📱 Tablet URLs (Use these on your tablets)

#### Main Overlay Control Panel:
- **Desktop Control**: http://192.168.0.189:3000
- **📱 Mobile Control**: http://192.168.0.189:3000/mobile

#### Pick/Ban Interface:
- **🎮 Player 1 Tablet**: http://192.168.0.189:5002/player/1
- **🎮 Player 2 Tablet**: http://192.168.0.189:5002/player/2
- **⚙️ Admin Panel**: http://192.168.0.189:5002/admin
- **📋 Pick/Ban Hub**: http://192.168.0.189:5002

### 🔧 Server Management

#### To Stop Servers:
```bash
./stop-smash-overlay.sh
./stop-pickban-server.sh
```

#### To Start Servers (Alternative Ports):
```bash
# Main overlay on port 3000
FLASK_RUN_PORT=3000 python3 app.py

# Pick/ban server on port 5002
./start-pickban-server.sh
```

### 📋 Pick/Ban Workflow

1. **Setup**: Open tablets to player URLs above
2. **Ban Phase**: Each player bans 3 stages (shows "BAN PHASE" header)
3. **Pick Phase**: After all bans, players can pick from remaining stages
4. **Reset**: Use admin panel to reset between sets

### 🎨 Features

- **Real-time Updates**: Interface updates automatically every 2 seconds
- **Visual Feedback**: Banned stages show red overlay, picked stages show green
- **Touch Optimized**: Designed for tablet touch interfaces
- **Network Accessible**: Works from any device on your WiFi network

### 🔍 Troubleshooting

If tablets can't connect:
1. **Check Network**: Ensure tablets are on same WiFi as computer
2. **Test Connection**: Try http://192.168.0.189:3000/mobile first
3. **Firewall**: Temporarily disable macOS firewall if needed
4. **Alternative Ports**: Use ports 8080 or 9000 if conflicts occur

### 🎮 Next Steps

- Test both URLs on your tablets
- The pick/ban data will be available for your stream overlay integration
- Use the admin panel to monitor and reset sessions

---
*Generated on: $(date)*
*Local IP: 192.168.0.189*
*Main Server Port: 3000*
*Pick/Ban Server Port: 5002*
