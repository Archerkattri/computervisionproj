import os
import pandas as pd
from flask import Blueprint, jsonify, request
from .config import upload_folder

fetch_annotations_bp = Blueprint('fetch_annotations', __name__)

def fetch_labels_from_csv(csv_file_name):
    csv_file_path = os.path.join(upload_folder, csv_file_name)
    try:
        df = pd.read_csv(csv_file_path)
        labels = df['label'].unique().tolist()  # Extract unique labels
        return jsonify({'labels': labels})
    except Exception as e:
        print(f"Error fetching labels: {str(e)}")
        return jsonify({'error': 'Failed to fetch labels'}), 500

@fetch_annotations_bp.route('/fetch-annotations', methods=['GET'])
def fetch_annotations():
    csv_file_name = request.args.get('csv_file_name')
    if not csv_file_name:
        return jsonify({'error': 'Missing csv_file_name'}), 400

    return fetch_labels_from_csv(csv_file_name)

def init_app(app):
    app.register_blueprint(fetch_annotations_bp)
