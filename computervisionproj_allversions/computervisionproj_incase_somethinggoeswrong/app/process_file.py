from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from __init__ import app, upload_folder  # Adjust according to your app's structure

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({'error': 'Invalid file name'}), 400
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 201

@app.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    return send_from_directory(upload_folder, filename)

# Add any other processing functions or routes here

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
