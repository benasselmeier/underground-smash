from flask import Flask, request, redirect, url_for, render_template, send_from_directory, make_response, jsonify
import os
import time
import json
import subprocess
import socket
from datetime import datetime, timedelta
from pathlib import Path
from core.state_backend import OverlayStateBackend

# Import for mDNS registration
try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    print("Zeroconf not available. Install with: pip install zeroconf")
app = Flask(__name__)
base_directory = 'text-files/'
themes_directory = 'themes/'
current_theme = {
    'scoreboard': 'greenhill',
    'casters': 'default',
    'vs-screen': 'default'
}
state_backend = OverlayStateBackend(
    text_base_dir=base_directory,
    db_path='runtime/state.db',
    mode=os.environ.get('STATE_BACKEND', 'sqlite')
)

# Global variable for mDNS service
zeroconf_service = None

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def register_mdns_service(port=5000):
    """Register the Flask app as an mDNS service"""
    global zeroconf_service
    
    if not ZEROCONF_AVAILABLE:
        print("⚠️  mDNS registration not available. Install zeroconf for mbsmash.local support")
        return None
    
    try:
        local_ip = get_local_ip()
        
        # Create service info
        service_info = ServiceInfo(
            "_http._tcp.local.",
            "mbsmash._http._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties={
                'path': '/',
                'mobile_path': '/mobile',
                'description': 'MB Smash Stream Control Panel'
            },
            server="mbsmash.local."
        )
        
        # Register the service
        zeroconf = Zeroconf()
        
        # Check if service is already registered and unregister first
        try:
            zeroconf.register_service(service_info)
            print(f"🌐 mDNS service registered!")
            if port == 80:
                print(f"📍 Desktop: http://mbsmash.local")
                print(f"📱 Mobile: http://mbsmash.local/mobile")
            else:
                print(f"📍 Desktop: http://mbsmash.local:{port}")
                print(f"📱 Mobile: http://mbsmash.local:{port}/mobile")
        except Exception as reg_error:
            print(f"⚠️  mDNS registration warning: {reg_error}")
            # Continue anyway - the service might still work
        
        return zeroconf
        
    except Exception as e:
        print(f"⚠️  Failed to register mDNS service: {e}")
        return None

def unregister_mdns_service():
    """Unregister the mDNS service"""
    global zeroconf_service
    if zeroconf_service:
        try:
            zeroconf_service.close()
            print("🌐 mDNS service unregistered")
        except Exception as e:
            print(f"⚠️  Error unregistering mDNS service: {e}")
        finally:
            zeroconf_service = None

# Set up static folder for images
app.static_folder = os.path.abspath('images')
app.static_url_path = '/images'
print(f"Static folder path: {app.static_folder}")  # Debug print

# Helper function to add cache headers to image responses
def add_cache_headers(response):
    # Set cache control headers (cache for 1 hour)
    response.headers['Cache-Control'] = 'public, max-age=3600'
    # Set expires header
    expires_time = datetime.utcnow() + timedelta(hours=1)
    response.headers['Expires'] = expires_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    # Set Last-Modified header to current time
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# Serve text files
@app.route('/text-files/<path:filename>')
def serve_text_file(filename):
    return send_from_directory(base_directory, filename)

# Serve resources files
@app.route('/resources/<path:filename>')
def serve_resource_file(filename):
    return send_from_directory('resources', filename)

# Serve fighter images with caching
@app.route('/images/fighter-ui-slice/<path:filename>')
def serve_fighter_image(filename):
    response = make_response(send_from_directory('images/fighter-ui-slice', filename))
    return add_cache_headers(response)

# Serve stylized fighter portraits with caching
@app.route('/images/fighter-portraits-stylized/cropped/<path:filename>')
def serve_stylized_portrait(filename):
    response = make_response(send_from_directory('images/fighter-portraits-stylized/cropped', filename))
    return add_cache_headers(response)

# Serve static images like Smash_Ball.png with caching
@app.route('/static/<path:filename>')
def serve_static_image(filename):
    response = make_response(send_from_directory('images', filename))
    return add_cache_headers(response)

def read_files_from_directory(directory):
    rel_dir = os.path.relpath(directory, base_directory).replace('\\', '/')
    if rel_dir == '.':
        rel_dir = ''
    return state_backend.read_directory(rel_dir)

def format_filename(filename):
    # Remove the file extension
    filename = os.path.splitext(filename)[0]
    # Replace dashes with spaces
    return filename.replace('-', ' ')

app.jinja_env.globals.update(format_filename=format_filename)


def read_text_file_safe(relative_path):
    """Read state safely via backend; return empty string on failure."""
    try:
        return state_backend.get(relative_path)
    except Exception:
        return ''


def build_overlay_state_payload():
    return {
        'info': {
            'theme': read_text_file_safe('info/Theme.txt'),
            'round': read_text_file_safe('info/Current-Round.txt'),
            'bracket': read_text_file_safe('info/Bracket-Name.txt'),
            'event': read_text_file_safe('info/Event-Info.txt'),
            'startgg': read_text_file_safe('info/StartGG-Slug.txt')
        },
        'player1': {
            'score': read_text_file_safe('player-1/Player1-Score.txt'),
            'name': read_text_file_safe('player-1/Enter Player 1 Name.txt'),
            'sponsor': read_text_file_safe('player-1/Player1-Sponsor.txt'),
            'fighter': read_text_file_safe('player-1/Player1-Fighter.txt'),
            'losers': read_text_file_safe('player-1/Player1-Losers.txt')
        },
        'player2': {
            'score': read_text_file_safe('player-2/Player2-Score.txt'),
            'name': read_text_file_safe('player-2/Enter Player 2 Name.txt'),
            'sponsor': read_text_file_safe('player-2/Player2-Sponsor.txt'),
            'fighter': read_text_file_safe('player-2/Player2-Fighter.txt'),
            'losers': read_text_file_safe('player-2/Player2-Losers.txt')
        },
        'casters': {
            'c1_sponsor': read_text_file_safe('casters/Caster1-Sponsor.txt'),
            'c1_name': read_text_file_safe('casters/Caster1-Name.txt'),
            'c2_sponsor': read_text_file_safe('casters/Caster2-Sponsor.txt'),
            'c2_name': read_text_file_safe('casters/Caster2-Name.txt')
        }
    }


def parse_player_id(raw_value):
    normalized = str(raw_value or '').strip().lower()
    if normalized in {'1', 'p1', 'player1', 'player-1'}:
        return 1
    if normalized in {'2', 'p2', 'player2', 'player-2'}:
        return 2
    return None


def player_path(player_id, suffix):
    if player_id == 1:
        return f'player-1/{suffix}'
    return f'player-2/{suffix}'


def read_score(player_id):
    raw_score = read_text_file_safe(player_path(player_id, f'Player{player_id}-Score.txt')).strip()
    try:
        return int(raw_score)
    except ValueError:
        return 0


def write_score(player_id, score):
    bounded = max(0, min(3, int(score)))
    state_backend.set(player_path(player_id, f'Player{player_id}-Score.txt'), str(bounded))
    return bounded


def swap_players_state():
    pairs = [
        ('player-1/Player1-Sponsor.txt', 'player-2/Player2-Sponsor.txt'),
        ('player-1/Enter Player 1 Name.txt', 'player-2/Enter Player 2 Name.txt'),
        ('player-1/Player1-Score.txt', 'player-2/Player2-Score.txt'),
        ('player-1/Player1-Fighter.txt', 'player-2/Player2-Fighter.txt'),
        ('player-1/Player1-Losers.txt', 'player-2/Player2-Losers.txt'),
    ]

    updates = {}
    for left, right in pairs:
        left_value = read_text_file_safe(left)
        right_value = read_text_file_safe(right)
        updates[left] = right_value
        updates[right] = left_value
    state_backend.bulk_set(updates)


def reset_scoreboard_state():
    state_backend.bulk_set({
        'player-1/Player1-Score.txt': '0',
        'player-2/Player2-Score.txt': '0',
        'player-1/Player1-Fighter.txt': 'Random',
        'player-2/Player2-Fighter.txt': 'Random',
    })


def new_round_state():
    state_backend.bulk_set({
        'player-1/Player1-Sponsor.txt': '',
        'player-1/Enter Player 1 Name.txt': '',
        'player-2/Player2-Sponsor.txt': '',
        'player-2/Enter Player 2 Name.txt': '',
    })
    reset_scoreboard_state()


def apply_form_updates(form_data, info_files, player_1_files, player_2_files, casters_files):
    updates = {}
    for directory, files in [
        ('info', info_files),
        ('player-1', player_1_files),
        ('player-2', player_2_files),
        ('casters', casters_files),
    ]:
        for filename in files:
            content = form_data.get(filename)
            if content is not None:
                updates[f'{directory}/{filename}'] = content

    if updates:
        state_backend.bulk_set(updates)


@app.route('/api/overlay-state')
def overlay_state():
    """Single payload for scoreboard-style overlays to reduce polling request count."""
    return jsonify(build_overlay_state_payload())


@app.route('/api/commands/score', methods=['POST'])
def command_score():
    data = request.get_json(silent=True) or request.form
    player_id = parse_player_id(data.get('player') or data.get('player_id'))
    if player_id is None:
        return jsonify({'success': False, 'error': 'player must be 1 or 2'}), 400

    if data.get('value') is not None:
        try:
            score = int(data.get('value'))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'value must be an integer'}), 400
    else:
        try:
            delta = int(data.get('delta', 0))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'delta must be an integer'}), 400
        score = read_score(player_id) + delta

    final_score = write_score(player_id, score)
    return jsonify({
        'success': True,
        'player': player_id,
        'score': final_score,
        'overlay_state': build_overlay_state_payload()
    })


@app.route('/api/commands/set-fighter', methods=['POST'])
def command_set_fighter():
    data = request.get_json(silent=True) or request.form
    player_id = parse_player_id(data.get('player') or data.get('player_id'))
    fighter = str(data.get('fighter', '')).strip()
    if player_id is None:
        return jsonify({'success': False, 'error': 'player must be 1 or 2'}), 400
    if not fighter:
        return jsonify({'success': False, 'error': 'fighter is required'}), 400

    state_backend.set(player_path(player_id, f'Player{player_id}-Fighter.txt'), fighter)
    return jsonify({'success': True, 'overlay_state': build_overlay_state_payload()})


@app.route('/api/commands/swap-players', methods=['POST'])
def command_swap_players():
    swap_players_state()
    return jsonify({'success': True, 'overlay_state': build_overlay_state_payload()})


@app.route('/api/commands/reset-scoreboard', methods=['POST'])
def command_reset_scoreboard():
    reset_scoreboard_state()
    return jsonify({'success': True, 'overlay_state': build_overlay_state_payload()})


@app.route('/api/commands/new-round', methods=['POST'])
def command_new_round():
    new_round_state()
    return jsonify({'success': True, 'overlay_state': build_overlay_state_payload()})

@app.route('/', methods=['GET', 'POST'])
def home():
    # Read the contents of the Fighters.txt file
    with open(os.path.join('resources', 'Fighters.txt'), 'r') as file:
        fighters = file.read().splitlines()
    info_files = read_files_from_directory(os.path.join(base_directory, 'info'))
    player_1_files = read_files_from_directory(os.path.join(base_directory, 'player-1'))
    player_2_files = read_files_from_directory(os.path.join(base_directory, 'player-2'))
    casters_files = read_files_from_directory(os.path.join(base_directory, 'casters'))

    if request.method == 'POST':
        apply_form_updates(request.form, info_files, player_1_files, player_2_files, casters_files)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Files updated successfully'}
        else:
            return redirect(url_for('home'))

    return render_template('home.html', info_files=info_files, player_1_files=player_1_files, player_2_files=player_2_files, casters_files=casters_files, fighters=fighters)

@app.route('/view/<filename>')
def view(filename):
    content = read_text_file_safe(filename)
    return '<form action="/update/{}" method="POST"><textarea name="content" rows="30" cols="100">{}</textarea><br><input type="submit" value="Update"></form>'.format(filename, content)

@app.route('/update/<filename>', methods=['POST'])
def update(filename):
    content = request.form['content']
    state_backend.set(filename, content)
    return redirect(url_for('view', filename=filename))

@app.route('/save-theme', methods=['POST'])
def save_theme():
    try:
        theme_content = request.form.get('Theme.txt')
        if theme_content:
            state_backend.set('info/Theme.txt', theme_content)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'status': 'success', 'message': 'Theme updated successfully'}
            else:
                return redirect(url_for('home'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'status': 'error', 'message': 'No theme data provided'}, 400
            else:
                return redirect(url_for('home'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'error', 'message': str(e)}, 500
        else:
            return redirect(url_for('home'))

@app.route('/mobile', methods=['GET', 'POST'])
def mobile():
    # Read the contents of the Fighters.txt file
    with open(os.path.join('resources', 'Fighters.txt'), 'r') as file:
        fighters = file.read().splitlines()
    info_files = read_files_from_directory(os.path.join(base_directory, 'info'))
    player_1_files = read_files_from_directory(os.path.join(base_directory, 'player-1'))
    player_2_files = read_files_from_directory(os.path.join(base_directory, 'player-2'))
    casters_files = read_files_from_directory(os.path.join(base_directory, 'casters'))

    if request.method == 'POST':
        apply_form_updates(request.form, info_files, player_1_files, player_2_files, casters_files)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Files updated successfully'}
        else:
            return redirect(url_for('mobile'))

    return render_template('mobile.html', info_files=info_files, player_1_files=player_1_files, player_2_files=player_2_files, casters_files=casters_files, fighters=fighters)

@app.route('/tablet-dashboard', methods=['GET', 'POST'])
def tablet_dashboard():
    # Read the contents of the Fighters.txt file
    with open(os.path.join('resources', 'Fighters.txt'), 'r') as file:
        fighters = file.read().splitlines()
    info_files = read_files_from_directory(os.path.join(base_directory, 'info'))
    player_1_files = read_files_from_directory(os.path.join(base_directory, 'player-1'))
    player_2_files = read_files_from_directory(os.path.join(base_directory, 'player-2'))
    casters_files = read_files_from_directory(os.path.join(base_directory, 'casters'))

    if request.method == 'POST':
        apply_form_updates(request.form, info_files, player_1_files, player_2_files, casters_files)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Files updated successfully'}
        else:
            return redirect(url_for('tablet_dashboard'))

    return render_template('tablet_dashboard.html', info_files=info_files, player_1_files=player_1_files, player_2_files=player_2_files, casters_files=casters_files, fighters=fighters)

@app.route('/debug-static')
def debug_static():
    static_folder = os.path.abspath(app.static_folder)
    return {
        'static_folder': static_folder,
        'static_url_path': app.static_url_path,
        'exists': os.path.exists(static_folder),
        'files': os.listdir(static_folder) if os.path.exists(static_folder) else []
    }

if __name__ == '__main__':
    import atexit
    import sys
    
    # Register cleanup function
    atexit.register(unregister_mdns_service)
    
    # Check if we should use port 80 (from environment variable)
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    
    # Register mDNS service
    zeroconf_service = register_mdns_service(port=port)
    
    try:
        # Disable reloader when using mDNS to avoid conflicts
        use_reloader = port != 80
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=use_reloader)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        unregister_mdns_service()
