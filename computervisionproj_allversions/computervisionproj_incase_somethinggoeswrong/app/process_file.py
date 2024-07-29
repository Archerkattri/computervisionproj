from flask import request, jsonify, send_from_directory
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
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 201

@app.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    return send_from_directory(upload_folder, filename)

# Add any other processing functions or routes here

if __name__ == '__main__':
    app.run(debug=True)
