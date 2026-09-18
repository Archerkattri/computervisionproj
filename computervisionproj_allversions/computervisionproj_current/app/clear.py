from flask import jsonify
import os
from .config import upload_folder

def init_app(app):
    @app.route('/clear', methods=['POST'])
    def clear_files():
        # Logic to clear uploaded files
        try:
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                os.remove(file_path)
            return jsonify({'message': 'All files cleared.'}), 200
        except Exception:
            app.logger.exception('Failed to clear files')
            return jsonify({'error': 'Failed to clear files'}), 500
