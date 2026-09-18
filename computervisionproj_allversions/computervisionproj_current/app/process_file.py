from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename, safe_join
import os
import requests
import logging
from .config import upload_folder

# Setup logging to a file
logging.basicConfig(filename='process_file.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def init_app(app):
    @app.route('/upload', methods=['OPTIONS', 'POST'])
    def upload():
        logging.info("Received upload request")

        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            logging.warning("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        if not filename:
            logging.warning("Invalid file name")
            return jsonify({'error': 'Invalid file name'}), 400
        file_path = os.path.join(upload_folder, filename)

        try:
            file.save(file_path)
            logging.info(f"File saved to {file_path}")

            # Determine file type
            file_extension = filename.split('.')[-1].lower()
            if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                # Process image
                processing_response = requests.post('http://localhost:5000/process-image', json={'image_name': filename})
                process_type = 'image'
            elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']:
                # Process video (assuming you have a similar endpoint for videos)
                processing_response = requests.post('http://localhost:5000/process-video', json={'file_name': filename})
                process_type = 'video'
            else:
                logging.warning(f"Unsupported file type: {file_extension}")
                return jsonify({'error': 'Unsupported file type'}), 400

            if processing_response.status_code != 200:
                logging.error(f"{process_type.capitalize()} processing failed: {processing_response.text}")
                return jsonify({'error': f'{process_type.capitalize()} processing failed', 'details': processing_response.text}), 500

            # Extract CSV file names from the response
            process_data = processing_response.json()
            all_csv_files = process_data.get('results', {})

            if not all_csv_files:
                logging.error(f"No CSV file names returned from /process-{process_type}")
                return jsonify({'error': 'No CSV file names returned'}), 500

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during processing request: {str(e)}")
            return jsonify({'error': 'Error during processing request'}), 500

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'file_name': filename,
            'csv_files': all_csv_files
        }), 201

    @app.route('/uploads/<filename>', methods=['GET'])
    def get_uploaded_file(filename):
        app.logger.info('File upload request received.')
        try:
            file_path = safe_join(upload_folder, filename)
        except Exception:
            file_path = None
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404

        app.logger.info('File uploaded successfully.')
        return send_from_directory(upload_folder, filename)
