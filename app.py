from flask import Flask, request, redirect, url_for, render_template
import os

app = Flask(__name__)
base_directory = 'text-files/'

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
        return redirect(url_for('home'))

    # Read the contents of the Fighters.txt file
    with open(os.path.join('resources', 'Fighters.txt'), 'r') as file:
        fighters = file.read().splitlines()

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

if __name__ == '__main__':
    app.run(debug=True)