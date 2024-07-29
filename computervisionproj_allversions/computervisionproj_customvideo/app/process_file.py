from flask import request, jsonify, send_from_directory
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
        file_path = os.path.join(upload_folder, file.filename)

        try:
            file.save(file_path)
            logging.info(f"File saved to {file_path}")

            # Determine file type
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                # Process image
                processing_response = requests.post('http://localhost:5000/process-image', json={'file_name': file.filename})
                process_type = 'image'
            elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']:
                # Process video
                processing_response = requests.post('http://localhost:5000/process-video', json={'file_name': file.filename})
                process_type = 'video'
            else:
                logging.warning(f"Unsupported file type: {file_extension}")
                return jsonify({'error': 'Unsupported file type'}), 400

            if processing_response.status_code != 200:
                logging.error(f"{process_type.capitalize()} processing failed: {processing_response.text}")
                return jsonify({'error': f'{process_type.capitalize()} processing failed', 'details': processing_response.text}), 500

            # Extract CSV file name from the response
            process_data = processing_response.json()
            csv_file_name = process_data.get('csv_file_name')

            if not csv_file_name:
                logging.error(f"No CSV file name returned from /process-{process_type}")
                return jsonify({'error': 'No CSV file name returned'}), 500

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during processing request: {str(e)}")
            return jsonify({'error': f'Error during processing request: {str(e)}'}), 500

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'file_name': file.filename,
            'csv_file_name': csv_file_name
        }), 201

    @app.route('/uploads/<filename>', methods=['GET'])
    def get_uploaded_file(filename):
        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404

        return send_from_directory(upload_folder, filename)
