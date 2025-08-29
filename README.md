# Underground Smash Overlay - Info, Instructions, Future Plans, To-Do List

## Instructions for Use:

**Important: for now, until I am able to package and deploy this to a web server, you'll need Python and Git installed.**

### Easy Startup (Recommended)

1. Open the `underground-smash-overlay` folder.
2. Double-click the `start-smash-overlay.sh` script or run it from a terminal:
   ```
   ./start-smash-overlay.sh
   ```
3. This will automatically start the application and provide URLs for both desktop and mobile access.
4. To stop the application, use the `stop-smash-overlay.sh` script:
   ```
   ./stop-smash-overlay.sh
   ```

### Accessing the Control Panel

**Desktop Control Panel:**
- Main URL: `http://127.0.0.1:5000` (localhost)
- Network URL: `http://[YOUR_IP]:5000` (access from other devices)

**📱 Mobile Control Panel:**
- Mobile URL: `http://[YOUR_IP]:5000/mobile`
- Optimized for phones and tablets
- Touch-friendly interface with all the same functionality as desktop
- Access from any device on the same WiFi network

**Note:** The start script will display your specific IP address and URLs when it runs.

### Manual Startup

If you prefer to start the application manually:

1. Open the `underground-smash-overlay` folder.
2. Right click somewhere in the folder and open a terminal window.
3. Run the setup script with the following command:
   ```
   bash dev-setup.sh
   ```

## Player/Caster Sponsors

The application now supports adding sponsor information for players and casters:

1. In the player and caster sections, you'll find optional fields for entering sponsor information.
2. The sponsor names will display in gold above the player/caster names in the overlays.
3. Leave the field blank if the player/caster doesn't have a sponsor.

## Visual Character Selection

The application now features a visual character selection interface:

1. Click the "Select Character" button for either player.
2. A grid of all available fighters will appear with images.
3. Click on the desired character to select them.
4. The selected character's image and name will appear below the selection button.
5. You can also select "Random" as a character option, which appears as the first choice in the character grid.

## Quick Actions

The application features a Quick Actions section for common operations:

1. **Score Adjustment**: Use the +1/-1 buttons to quickly adjust player scores.
2. **Swap Players**: The swap button (⇄) exchanges player information between Player 1 and Player 2.
3. **Reset Scoreboard**: The reset button (↺) sets both player scores to 0 and characters to "Random".
4. **New Round**: The new round button (🏁) clears all player data for a fresh start.
5. **Save Changes**: The save button (💾) manually saves all current form values.

## Mobile Control Panel Features

The mobile interface (`/mobile`) provides all the functionality of the desktop version, optimized for touch devices:

- **Touch-optimized character selection** with large, easy-to-tap character portraits
- **Quick score adjustment** with prominent +/- buttons
- **Auto-saving** - changes are saved automatically as you type or make selections
- **Responsive design** that works on phones, tablets, and other mobile devices
- **Same data sync** - changes made on mobile instantly appear on desktop and vice versa
- **Network access** - control your stream from anywhere on the same WiFi network

### Mobile Usage Tips:
- Add the mobile URL to your phone's home screen for quick access
- The interface works in both portrait and landscape orientations
- All quick actions are prominently displayed at the top for easy access
- Character selection uses a scrollable grid optimized for touch

## Future Plans:

- Web UI on an actual website, so we can access it from anywhere
- Theme switching capability
- Modular theme organization
- Custom logo support

## To-Do List:
- Fix graphics for the following fighters

    Vs. Screen:
    - Luigi


# Development