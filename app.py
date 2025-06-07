from flask import Flask, request, redirect, url_for, render_template, send_from_directory, make_response
import os
import time
from datetime import datetime, timedelta

from pathlib import Path
app = Flask(__name__)
base_directory = 'text-files/'

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

# Serve static images like Smash_Ball.png with caching
@app.route('/static/<path:filename>')
def serve_static_image(filename):
    response = make_response(send_from_directory('images', filename))
    return add_cache_headers(response)

def read_files_from_directory(directory):
    print(f"Reading files from directory: {directory}")  # Debug statement
    files = sorted(os.listdir(directory))
    file_contents = {}
    for file in files:
        try:
            with open(os.path.join(directory, file), 'r') as f:
                file_contents[file] = f.read()
        except UnicodeDecodeError:
            print(f"Skipping file {file} because it could not be decoded")
    print(f"Files read from {directory}: {file_contents.keys()}")  # Debug statement
    return file_contents

def format_filename(filename):
    # Remove the file extension
    filename = os.path.splitext(filename)[0]
    # Replace dashes with spaces
    return filename.replace('-', ' ')

app.jinja_env.globals.update(format_filename=format_filename)

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
        for directory, files in [('info', info_files), ('player-1', player_1_files), ('player-2', player_2_files), ('casters', casters_files)]:
            for file in files:
                content = request.form.get(file)
                if content is not None:
                    with open(os.path.join(base_directory, directory, file), 'w') as f:
                        f.write(content)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Files updated successfully'}
        else:
            return redirect(url_for('home'))

    return render_template('home.html', info_files=info_files, player_1_files=player_1_files, player_2_files=player_2_files, casters_files=casters_files, fighters=fighters)

@app.route('/view/<filename>')
def view(filename):
    with open(os.path.join(base_directory, filename), 'r') as f:
        content = f.read()
    return '<form action="/update/{}" method="POST"><textarea name="content" rows="30" cols="100">{}</textarea><br><input type="submit" value="Update"></form>'.format(filename, content)

@app.route('/update/<filename>', methods=['POST'])
def update(filename):
    content = request.form['content']
    with open(os.path.join(base_directory, filename), 'w') as f:
        f.write(content)
    return redirect(url_for('view', filename=filename))

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
    app.run(debug=True, host='0.0.0.0')