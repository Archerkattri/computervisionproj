# __init__.py

import os
import logging

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from .process_image import init_app as init_process_image
from .search_annotation import init_app as init_search_annotation
from .generate_image import init_app as init_generate_image
from .fetch_annotation import init_app as init_fetch_annotations
from .generate_video import init_app as init_generate_video  # Added import
from .config import upload_folder

# Setup logging
logging.basicConfig(filename='init.log', level=logging.DEBUG,  # Set logging level to DEBUG
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SocketIO globally
socketio = SocketIO()

def create_app():
    app = Flask(__name__, static_folder='../build', static_url_path='/')
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    socketio.init_app(app)

    # Define upload folder (you already have this in config.py)
    os.makedirs(upload_folder, exist_ok=True)
    logging.info("Upload folder ensured at: {}".format(upload_folder))

    # Initialize application modules
    init_process_image(app)
    init_search_annotation(app)
    init_generate_image(app)
    init_fetch_annotations(app)  # Initialize fetch_annotations module
    init_generate_video(app)  # Initialize generate_video module

    # Additional routes initialization
    init_routes(app)

    return app

def init_routes(app):
    # Import and initialize routes
    from .process_file import init_app as init_process_file
    from .process_video import init_app as init_process_video
    from .clear import init_app as init_clear
    from .get_coco_categories import init_app as init_get_coco_categories

    init_process_file(app)
    init_process_video(app)
    init_clear(app)
    init_get_coco_categories(app)

    @app.route('/')
    def serve_index():
        logging.info("Serving index.html")
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(upload_folder, filename)

    @app.route('/<path:path>')
    def serve_static(path):
        logging.info(f"Serving static file: {path}")
        return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app = create_app()
    app.debug = True  # Enable Flask debug mode
    logging.info("Starting Flask app in debug mode")
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, allow_unsafe_werkzeug=True)
