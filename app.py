from flask import Flask, request, redirect, url_for, render_template
import os

app = Flask(__name__)
directory = 'text-files/'

@app.route('/', methods=['GET', 'POST'])
def home():
    directory = 'text-files'
    files = sorted(os.listdir(directory))
    file_names = {format_filename(file): file for file in files}
    file_contents = {}
    for formatted_name, original_name in file_names.items():
        try:
            with open(os.path.join(directory, original_name), 'r') as f:
                file_contents[formatted_name] = f.read()
        except UnicodeDecodeError:
            print(f"Skipping file {original_name} because it could not be decoded")
    if request.method == 'POST':
        for formatted_name, original_name in file_names.items():
            content = request.form.get(formatted_name)
            if content is not None:
                with open(os.path.join(directory, original_name), 'w') as f:
                    f.write(content)
        return redirect(url_for('home'))

    # Read the contents of the Fighters.txt file
    with open(os.path.join('resources', 'Fighters.txt'), 'r') as file:
        fighters = file.read().splitlines()

    return render_template('home.html', files=file_contents, fighters=fighters)

@app.route('/view/<filename>')
def view(filename):
    with open(os.path.join(directory, filename), 'r') as f:
        content = f.read()
    return '<form action="/update/{}" method="POST"><textarea name="content" rows="30" cols="100">{}</textarea><br><input type="submit" value="Update"></form>'.format(filename, content)

@app.route('/update/<filename>', methods=['POST'])
def update(filename):
    content = request.form['content']
    with open(os.path.join(directory, filename), 'w') as f:
        f.write(content)
    return redirect(url_for('view', filename=filename))

def format_filename(filename):
    # Remove the file extension
    filename = os.path.splitext(filename)[0]
    # Replace dashes with spaces
    filename = filename.replace('-', ' ')
    # Capitalize each word
    filename = filename.title()
    return filename

if __name__ == '__main__':
    app.run(debug=True)