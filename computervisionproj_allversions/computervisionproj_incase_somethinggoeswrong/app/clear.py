import os
from flask import jsonify
from __init__ import upload_folder  # Adjust according to your app's structure

def clear_files():
    try:
        # List all files in the upload folder
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            # Check if it's a file and delete it
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted file: {file_path}")

        print("All files cleared successfully.")
        return jsonify({'message': 'Files cleared successfully'}), 200

    except Exception as e:
        print(f"Error clearing files: {e}")
        return jsonify({'error': 'An error occurred while clearing files.'}), 500
