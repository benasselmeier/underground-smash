#!/usr/bin/env python3
"""
Pick/Ban Server for Underground Smash Overlay
Dedicated server for player pick/ban interfaces on tablets
"""

from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
import os
import json
import socket
from datetime import datetime
from pathlib import Path

# Import for mDNS registration
try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    print("Zeroconf not available. Install with: pip install zeroconf")

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / 'images'
RESOURCES_DIR = BASE_DIR / 'resources'
TEXT_FILES_DIR = BASE_DIR / 'text-files'


@app.after_request
def add_cors_headers(response):
    """Allow overlay pages hosted on other local origins to call this API."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Configuration
PICKBAN_PORT = 5002
GAME1_PATTERN = [1, 2, 1]
POSTGAME_WINNER_STRIKES = 3
current_session = {}

# Global variable for mDNS service
zeroconf_service = None

def load_stages():
    """Load stages from the resources file with categories"""
    stages_file = RESOURCES_DIR / 'Stages.txt'
    stage_data = {'starters': [], 'counterpicks': []}
    
    if stages_file.exists():
        with open(stages_file, 'r') as f:
            current_category = 'starters'
            for line in f:
                line = line.strip()
                if not line or line.startswith('//'):
                    if 'counterpick' in line.lower():
                        current_category = 'counterpicks'
                    continue
                
                stage_data[current_category].append(line)
        
        # Return flat list for compatibility, but keep category info
        all_stages = stage_data['starters'] + stage_data['counterpicks']
        return all_stages, stage_data
    else:
        # Fallback stages if file doesn't exist
        starters = [
            'Battlefield',
            'Small Battlefield', 
            'Pokemon Stadium 2',
            'Town and City',
            'Smashville'
        ]
        counterpicks = [
            'Final Destination',
            'Hollow Bastion',
            'Kalos Pokemon League'
        ]
        stage_data = {'starters': starters, 'counterpicks': counterpicks}
        return starters + counterpicks, stage_data


def read_files_from_directory(directory_path):
    """Read all UTF-8 decodable files in a directory into a dict."""
    file_contents = {}
    if not Path(directory_path).exists():
        return file_contents

    for file_name in sorted(os.listdir(directory_path)):
        file_path = Path(directory_path) / file_name
        if not file_path.is_file():
            continue
        try:
            file_contents[file_name] = file_path.read_text()
        except UnicodeDecodeError:
            continue
    return file_contents

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def register_mdns_service():
    """Register the Pick/Ban server as an mDNS service"""
    global zeroconf_service
    
    if not ZEROCONF_AVAILABLE:
        print("⚠️  mDNS registration not available. Install zeroconf for pickban.local support")
        return None
    
    try:
        local_ip = get_local_ip()
        
        service_info = ServiceInfo(
            "_http._tcp.local.",
            "pickban._http._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=PICKBAN_PORT,
            properties={
                'path': '/',
                'player1_path': '/player/1',
                'player2_path': '/player/2',
                'description': 'MB Smash Pick/Ban Interface'
            },
            server="pickban.local."
        )
        
        zeroconf = Zeroconf()
        
        try:
            zeroconf.register_service(service_info)
            print(f"🎯 Pick/Ban mDNS service registered!")
            print(f"🎮 Player 1: http://pickban.local:{PICKBAN_PORT}/player/1")
            print(f"🎮 Player 2: http://pickban.local:{PICKBAN_PORT}/player/2")
        except Exception as reg_error:
            print(f"⚠️  mDNS registration warning: {reg_error}")
        
        return zeroconf
        
    except Exception as e:
        print(f"⚠️  Failed to register mDNS service: {e}")
        return None

# Initialize stage list
stage_list, stage_categories = load_stages()


def player_key(player_id):
    return f'player{player_id}'


def opponent(player_id):
    return 2 if player_id == 1 else 1


def create_session(first_striker=1):
    """Create a fresh rules-compliant Smash Ultimate stage select session."""
    first = 1 if first_striker not in [1, 2] else first_striker
    return {
        'stage_list': stage_list,
        'stage_categories': stage_categories,
        'banned_stages': [],
        'stage_strikes': [],
        'picked_stage': None,
        'picked_by': None,
        'game_number': 1,
        'flow_phase': 'game1_strike',   # game1_strike | postgame_strike | postgame_pick | stage_selected
        'current_phase': 'banning',     # compatibility field for existing UIs
        'current_player': first,
        'first_striker': first,
        'winner_player': None,
        'loser_player': None,
        'game1_pattern': GAME1_PATTERN,
        'game1_step_index': 0,
        'game1_step_strikes_done': 0,
        'strikes_used': {'player1': 0, 'player2': 0},
        'strikes_target': {'player1': 0, 'player2': 0},
        'bans_used': {'player1': 0, 'player2': 0},  # compatibility alias
        'max_bans': POSTGAME_WINNER_STRIKES,         # compatibility alias
        'selectable_stages': [],
        'turn_message': '',
        'phase_message': '',
        'allow_counterpicks': False,
        'generic_turn_mode': False
    }


def get_allowed_stage_pool(session):
    if session['flow_phase'] == 'game1_strike':
        return session['stage_categories']['starters']
    return session['stage_list']


def get_selectable_stages(session):
    if session['flow_phase'] == 'stage_selected':
        return []

    pool = get_allowed_stage_pool(session)
    return [s for s in pool if s not in session['banned_stages']]


def current_game1_step_player(session):
    step = session['game1_step_index']
    first = session['first_striker']
    second = opponent(first)
    return first if step in [0, 2] else second


def update_derived_session_fields(session):
    """Populate compatibility/UI helper fields after each state transition."""
    session['bans_used'] = dict(session['strikes_used'])

    if session['flow_phase'] == 'game1_strike':
        session['current_phase'] = 'banning'
        session['allow_counterpicks'] = False
        session['selectable_stages'] = get_selectable_stages(session)
        step = session['game1_step_index']
        first = session['first_striker']
        second = opponent(first)
        pattern = session['game1_pattern']
        session['current_player'] = current_game1_step_player(session)
        session['strikes_target'] = {
            player_key(first): 2,   # first player strikes in step 0 and step 2
            player_key(second): 2   # second player strikes twice in step 1
        }
        session['turn_message'] = f"Player {session['current_player']} strike turn"
        session['phase_message'] = (
            f"Game 1 starter striking ({step + 1}/{len(pattern)}): "
            f"P{first} strikes {pattern[0]}, P{second} strikes {pattern[1]}, P{first} strikes {pattern[2]}"
        )
    elif session['flow_phase'] == 'postgame_strike':
        session['current_phase'] = 'banning'
        session['allow_counterpicks'] = True
        session['selectable_stages'] = get_selectable_stages(session)
        winner = session['winner_player']
        session['strikes_target'] = {'player1': 0, 'player2': 0}
        if winner in [1, 2]:
            session['current_player'] = winner
            session['strikes_target'][player_key(winner)] = POSTGAME_WINNER_STRIKES
            session['turn_message'] = f"Player {winner} (winner) strikes {POSTGAME_WINNER_STRIKES}"
            session['phase_message'] = "Post-game: winner strikes 3 stages, then loser picks."
        else:
            session['current_player'] = None
            session['turn_message'] = "No winner declared: players strike any 3 stages, then pick."
            session['phase_message'] = "Generic post-game flow: strike any 3 stages, then pick."
    elif session['flow_phase'] == 'postgame_pick':
        session['current_phase'] = 'picking'
        session['allow_counterpicks'] = True
        session['selectable_stages'] = get_selectable_stages(session)
        loser = session['loser_player']
        session['current_player'] = loser if loser in [1, 2] else None
        session['strikes_target'] = {'player1': 0, 'player2': 0}
        if loser in [1, 2]:
            session['turn_message'] = f"Player {loser} (loser) picks the stage"
            session['phase_message'] = "Post-game: loser picks from remaining stages."
        else:
            session['turn_message'] = "No winner declared: either player may pick from remaining stages."
            session['phase_message'] = "Generic post-game flow: pick from remaining stages."
    else:
        session['current_phase'] = 'complete'
        session['current_player'] = None
        session['allow_counterpicks'] = session['game_number'] > 1
        session['selectable_stages'] = []
        session['strikes_target'] = {'player1': 0, 'player2': 0}
        session['turn_message'] = "Stage selected"
        session['phase_message'] = f"Game {session['game_number']} stage selected."


def advance_after_strike(session):
    """Advance state machine after a successful strike."""
    if session['flow_phase'] == 'game1_strike':
        session['game1_step_strikes_done'] += 1
        step_idx = session['game1_step_index']
        strikes_required = session['game1_pattern'][step_idx]

        if session['game1_step_strikes_done'] >= strikes_required:
            session['game1_step_index'] += 1
            session['game1_step_strikes_done'] = 0

        if session['game1_step_index'] >= len(session['game1_pattern']):
            remaining = [s for s in session['stage_categories']['starters'] if s not in session['banned_stages']]
            if remaining:
                session['picked_stage'] = remaining[0]
                session['picked_by'] = None
            session['flow_phase'] = 'stage_selected'
    elif session['flow_phase'] == 'postgame_strike':
        winner = session['winner_player']
        if winner in [1, 2]:
            winner_key = player_key(winner)
            if session['strikes_used'][winner_key] >= POSTGAME_WINNER_STRIKES:
                session['flow_phase'] = 'postgame_pick'
        else:
            if len(session['banned_stages']) >= POSTGAME_WINNER_STRIKES:
                session['flow_phase'] = 'postgame_pick'

    update_derived_session_fields(session)


def reset_for_next_game(session, winner_player=None):
    """Start post-game striking for the next game."""
    winner = winner_player if winner_player in [1, 2] else None
    loser = opponent(winner) if winner in [1, 2] else None
    session['game_number'] += 1
    session['winner_player'] = winner
    session['loser_player'] = loser
    session['banned_stages'] = []
    session['stage_strikes'] = []
    session['picked_stage'] = None
    session['picked_by'] = None
    session['strikes_used'] = {'player1': 0, 'player2': 0}
    session['flow_phase'] = 'postgame_strike'
    session['game1_step_index'] = 0
    session['game1_step_strikes_done'] = 0
    session['generic_turn_mode'] = winner is None
    update_derived_session_fields(session)


current_session = create_session(first_striker=1)
update_derived_session_fields(current_session)

# Set up static folders
app.static_folder = str(IMAGES_DIR)
app.static_url_path = '/images'


@app.route('/resources/<path:filename>')
def serve_resource_file(filename):
    """Serve resources (fonts, txt, etc.) for pick/ban templates."""
    return send_from_directory(str(RESOURCES_DIR), filename)


@app.route('/images/<path:filename>')
def serve_image_file(filename):
    """Serve image assets for pick/ban templates."""
    return send_from_directory(str(IMAGES_DIR), filename)

@app.route('/')
def index():
    """Main landing page for pick/ban server"""
    local_ip = get_local_ip()
    return render_template('pickban_index.html', 
                         local_ip=local_ip, 
                         port=PICKBAN_PORT)

@app.route('/player/<int:player_id>')
def player_interface(player_id):
    """Player pick/ban interface"""
    if player_id not in [1, 2]:
        return "Invalid player ID", 404
    
    return render_template('pickban_player.html', 
                         player_id=player_id,
                         session=current_session)

@app.route('/api/session')
def get_session():
    """Get current session state"""
    return jsonify(current_session)

@app.route('/api/ban_stage', methods=['POST'])
def ban_stage():
    """Alias for striking a stage (kept for backward compatibility)."""
    return strike_stage()


@app.route('/api/strike_stage', methods=['POST'])
def strike_stage():
    """Strike a stage according to current rules phase."""
    data = request.get_json()
    stage_name = data.get('stage')
    player_id = data.get('player_id')

    if current_session['flow_phase'] not in ['game1_strike', 'postgame_strike']:
        return jsonify({'success': False, 'error': 'Not in strike phase'})

    if current_session['current_player'] in [1, 2] and player_id != current_session['current_player']:
        return jsonify({'success': False, 'error': f'Not player {player_id} turn'})

    selectable = get_selectable_stages(current_session)
    if stage_name not in selectable:
        return jsonify({'success': False, 'error': 'Cannot strike this stage'})

    pkey = player_key(player_id)
    current_session['banned_stages'].append(stage_name)
    current_session['stage_strikes'].append({
        'stage': stage_name,
        'player_id': player_id,
        'phase': current_session['flow_phase'],
        'game_number': current_session['game_number']
    })
    current_session['strikes_used'][pkey] += 1

    advance_after_strike(current_session)
    return jsonify({'success': True, 'session': current_session})

@app.route('/api/pick_stage', methods=['POST'])
def pick_stage():
    """Pick a stage in post-game pick phase."""
    data = request.get_json()
    stage_name = data.get('stage')
    player_id = data.get('player_id')

    if current_session['flow_phase'] != 'postgame_pick':
        return jsonify({'success': False, 'error': 'Not in pick phase'})

    if current_session['current_player'] in [1, 2] and player_id != current_session['current_player']:
        return jsonify({'success': False, 'error': f'Not player {player_id} turn'})

    selectable = get_selectable_stages(current_session)
    if stage_name not in selectable:
        return jsonify({'success': False, 'error': 'Cannot pick this stage'})

    current_session['picked_stage'] = stage_name
    current_session['picked_by'] = player_id
    current_session['flow_phase'] = 'stage_selected'
    update_derived_session_fields(current_session)
    return jsonify({'success': True, 'session': current_session})


@app.route('/api/set_first_striker', methods=['POST'])
def set_first_striker():
    """Set who strikes first for game 1 and restart game 1 striking."""
    global current_session
    data = request.get_json() or {}
    first_player = data.get('first_player', 1)
    if first_player not in [1, 2]:
        return jsonify({'success': False, 'error': 'first_player must be 1 or 2'})

    current_session = create_session(first_striker=first_player)
    update_derived_session_fields(current_session)
    return jsonify({'success': True, 'session': current_session})


@app.route('/api/start_next_game', methods=['POST'])
def start_next_game():
    """Begin post-game stage flow after reporting previous game winner."""
    data = request.get_json() or {}
    winner_player = data.get('winner_player')
    if winner_player not in [1, 2]:
        return jsonify({'success': False, 'error': 'winner_player must be 1 or 2'})

    reset_for_next_game(current_session, winner_player)
    return jsonify({'success': True, 'session': current_session})


@app.route('/api/start_next_game_generic', methods=['POST'])
def start_next_game_generic():
    """Begin next game stage flow with no winner declared (shared control mode)."""
    reset_for_next_game(current_session, winner_player=None)
    return jsonify({'success': True, 'session': current_session})


@app.route('/api/gentleman_pick', methods=['POST'])
def gentleman_pick():
    """Set stage by mutual agreement (gentleman's)."""
    data = request.get_json() or {}
    stage_name = data.get('stage')
    player_id = data.get('player_id')
    if stage_name not in current_session['stage_list']:
        return jsonify({'success': False, 'error': 'Invalid stage'})

    current_session['picked_stage'] = stage_name
    current_session['picked_by'] = player_id if player_id in [1, 2] else None
    current_session['flow_phase'] = 'stage_selected'
    update_derived_session_fields(current_session)
    return jsonify({'success': True, 'session': current_session})

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset the pick/ban session"""
    global current_session
    current_session = create_session(first_striker=current_session.get('first_striker', 1))
    update_derived_session_fields(current_session)
    return jsonify({'success': True, 'session': current_session})

@app.route('/admin')
def admin_panel():
    """Admin panel for managing pick/ban session"""
    return render_template('pickban_admin.html', session=current_session)


@app.route('/tablet-dashboard', methods=['GET', 'POST'])
def tablet_dashboard():
    """Serve the main scoreboard tablet dashboard from pick/ban server."""
    fighters_path = RESOURCES_DIR / 'Fighters.txt'
    fighters = fighters_path.read_text().splitlines() if fighters_path.exists() else []
    info_files = read_files_from_directory(TEXT_FILES_DIR / 'info')
    player_1_files = read_files_from_directory(TEXT_FILES_DIR / 'player-1')
    player_2_files = read_files_from_directory(TEXT_FILES_DIR / 'player-2')
    casters_files = read_files_from_directory(TEXT_FILES_DIR / 'casters')

    if request.method == 'POST':
        for directory, files in [
            ('info', info_files),
            ('player-1', player_1_files),
            ('player-2', player_2_files),
            ('casters', casters_files),
        ]:
            for file_name in files:
                content = request.form.get(file_name)
                if content is not None:
                    file_path = TEXT_FILES_DIR / directory / file_name
                    file_path.write_text(content)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Files updated successfully'})
        return redirect(url_for('tablet_dashboard'))

    return render_template(
        'tablet_dashboard.html',
        info_files=info_files,
        player_1_files=player_1_files,
        player_2_files=player_2_files,
        casters_files=casters_files,
        fighters=fighters
    )


@app.route('/overlays/pick-ban')
@app.route('/overlay/stage-bar')
def stage_bar_overlay():
    """Transparent bottom-bar overlay showing current stage strikes/pick."""
    return send_from_directory('overlays/pick-ban', 'pickban_overlay.html')

# Serve CSS files from templates directory
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('templates', filename)

def unregister_mdns_service():
    """Unregister the mDNS service"""
    global zeroconf_service
    if zeroconf_service:
        try:
            zeroconf_service.close()
            print("🎯 Pick/Ban mDNS service unregistered")
        except Exception as e:
            print(f"⚠️  Error unregistering mDNS service: {e}")
        finally:
            zeroconf_service = None

if __name__ == '__main__':
    debug_mode = os.environ.get('PICKBAN_DEBUG', '0') == '1'
    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

    print("🎯 Starting Underground Smash Pick/Ban Server...")
    print(f"📱 Server will be available on port {PICKBAN_PORT}")
    
    # Register mDNS once. In debug reloader mode, only the child process should register.
    if (not debug_mode) or is_reloader_child:
        zeroconf_service = register_mdns_service()
    
    try:
        local_ip = get_local_ip()
        print(f"🌐 Local access:")
        print(f"   📍 Main page: http://{local_ip}:{PICKBAN_PORT}")
        print(f"   🎮 Player 1: http://{local_ip}:{PICKBAN_PORT}/player/1")
        print(f"   🎮 Player 2: http://{local_ip}:{PICKBAN_PORT}/player/2")
        print(f"   ⚙️  Admin: http://{local_ip}:{PICKBAN_PORT}/admin")
        print("🚀 Starting server...")
        
        app.run(
            host='0.0.0.0',
            port=PICKBAN_PORT,
            debug=debug_mode,
            use_reloader=debug_mode
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Pick/Ban server...")
    finally:
        unregister_mdns_service()
