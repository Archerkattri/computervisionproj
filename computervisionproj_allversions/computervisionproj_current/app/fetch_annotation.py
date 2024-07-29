import os
import pandas as pd
from flask import Blueprint, jsonify, request
from .config import upload_folder

fetch_annotations_bp = Blueprint('fetch_annotations', __name__)

def fetch_labels_from_csv(file_names):
    labels_set = set()

    for csv_file_name in file_names:
        csv_file_path = os.path.join(upload_folder, csv_file_name)

        try:
            df = pd.read_csv(csv_file_path)

            # Extract labels from 'labels' column for detection files
            if 'labels' in df.columns:
                labels = df['labels'].unique().tolist()
                labels_set.update(labels)
            else:
                # Unsupported file format
                continue

        except Exception as e:
            print(f"Error fetching labels from {csv_file_name}: {str(e)}")
            return jsonify({'error': f'Failed to fetch labels from {csv_file_name}'}), 500

    return jsonify({'labels': list(labels_set)})

@fetch_annotations_bp.route('/fetch-annotations', methods=['POST'])
def fetch_annotations():
    data = request.get_json()
    csv_file_names = data.get('csv_file_names', [])

    if not csv_file_names:
        return jsonify({'error': 'No csv_file_names provided'}), 400

    return fetch_labels_from_csv(csv_file_names)

def init_app(app):
    app.register_blueprint(fetch_annotations_bp)
