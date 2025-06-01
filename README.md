# Underground Smash Overlay - Info, Instructions, Future Plans, To-Do List

## Instructions for Use:

**Important: for now, until I am able to package and deploy this to a web server, you'll need Python and Git installed.**

### Easy Startup (Recommended)

1. Open the `underground-smash-overlay` folder.
2. Double-click the `start-smash-overlay.sh` script or run it from a terminal:
   ```
   ./start-smash-overlay.sh
   ```
3. This will automatically start the application and open it in your default browser.
4. To stop the application, use the `stop-smash-overlay.sh` script:
   ```
   ./stop-smash-overlay.sh
   ```

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