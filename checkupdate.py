from flask import Flask, request, redirect, url_for, flash, render_template_string, session
from werkzeug.utils import secure_filename
import os
import stat
import shutil
import zipfile
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit max upload size to 16MB

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'txt', 'py', 'html', 'css', 'js', 'md', 'xlsm', 'pdf'}

CURRENT_VERSION = '1.0.1'
GITHUB_API_URL = "https://api.github.com/repos/yourusername/yourrepo/releases/latest"  # Update with your repo

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files_and_folders(base_folder):
    items = []
    for root, dirs, files in os.walk(base_folder):
        for dir_name in dirs:
            folder_path = os.path.relpath(os.path.join(root, dir_name), base_folder)
            folder_perm = stat.filemode(os.stat(os.path.join(root, dir_name)).st_mode)
            items.append({'type': 'folder', 'name': folder_path, 'permissions': folder_perm})
        for filename in files:
            file_path = os.path.relpath(os.path.join(root, filename), base_folder)
            file_ext = os.path.splitext(filename)[1][1:]
            file_perm = stat.filemode(os.stat(os.path.join(root, filename)).st_mode)
            items.append({'type': 'file', 'name': file_path, 'extension': file_ext, 'permissions': file_perm})
    return items



@app.route('/', methods=['POST'])
def upload_file_action():
    if 'file' not in request.files:
        flash('No file selected. Please choose a file to upload.')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No file selected. Please choose a file to upload.')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('index'))
    else:
        flash('File type not allowed. Please upload a valid file.')
        return redirect(request.url)

@app.route('/perform_action', methods=['POST'])
def perform_action():
    action = request.form['action']
    selected_items = request.form.getlist('selected_items')

    if action == 'Delete':
        for name in selected_items:
            item_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
            if os.path.isfile(item_path):
                os.remove(item_path)
                flash(f'File {name} successfully deleted.')
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                flash(f'Folder {name} successfully deleted.')

    return redirect(url_for('index'))

@app.route('/view/<path:filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        flash('File not found.')
        return redirect(url_for('index'))

@app.route('/view_folder/<path:foldername>')
def view_folder(foldername):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], foldername)

    if os.path.exists(folder_path):
        items = get_files_and_folders(folder_path)
        return render_template_string('''
        <!doctype html>
        <title>Folder Details</title>
        <h1>Details of Folder: {{ foldername }}</h1>

        <h2>Files and Subfolders</h2>
        <table border="1">
            <tr>
                <th>#</th>
                <th>Type</th>
                <th>Name</th>
                <th>File Extension</th>
                <th>Permissions</th>
                <th>Actions</th>
            </tr>
            {% for item in items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.type }}</td>
                <td>
                    {% if item.type == 'file' %}
                        <a href="{{ url_for('view_file', filename=item.name) }}">{{ item.name }}</a>
                    {% else %}
                        <a href="{{ url_for('view_folder', foldername=item.name) }}">{{ item.name }}</a>
                    {% endif %}
                </td>
                <td>{{ item.extension if item.type == 'file' else '-' }}</td>
                <td>{{ item.permissions }}</td>
                <td>
                    <form method="POST" action="{{ url_for('perform_action') }}" style="display:inline;">
                        <input type="submit" name="action" value="Delete" onclick="return confirm('Are you sure you want to delete this item?');">
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>

        <a href="{{ url_for('index') }}">Back to Main</a>
        ''', items=items, foldername=foldername)
    else:
        flash('Folder not found.')
        return redirect(url_for('index'))

@app.route('/zip/<path:filename>', methods=['POST'])
def zip_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    zip_path = f"{file_path}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(file_path, os.path.basename(file_path))

    flash(f'File {filename} successfully zipped.')
    return redirect(url_for('index'))

@app.route('/unzip/<path:filename>', methods=['POST'])
def unzip_file(filename):
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    extract_folder = os.path.splitext(zip_path)[0]  # Removing .zip extension

    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(extract_folder)

    flash(f'File {filename} successfully unzipped.')
    return redirect(url_for('index'))

@app.route('/download/<path:filename>', methods=['POST'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
