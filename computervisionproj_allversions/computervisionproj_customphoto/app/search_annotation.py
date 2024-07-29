# search_annotation.py
import os
import pandas as pd
from flask import Blueprint, jsonify, request
from .config import upload_folder

search_annotation_bp = Blueprint('search_annotation', __name__)

@search_annotation_bp.route('/search', methods=['POST'])
def search_annotation():
    data = request.json
    filename = data.get('filename')
    query = data.get('query')

    print(f"Received search request for '{query}' in {filename}")

    # Load CSV for the filename
    temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
    if not os.path.exists(temp_csv_path):
        print(f"CSV file not found: {temp_csv_path}")
        return jsonify({'error': 'CSV file not found'}), 404

    try:
        # Read CSV and filter based on query
        df = pd.read_csv(temp_csv_path)
        matched_boxes = df[df['label'].str.contains(query, case=False, na=False)]

        if matched_boxes.empty:
            return jsonify({'error': f'The annotation "{query}" is not available in this file.'}), 404

        # Collect bounding box data
        box_data = matched_boxes['bounding_boxes'].tolist()

        return jsonify({'boxes': box_data}), 200

    except pd.errors.EmptyDataError:
        print("CSV file is empty.")
        return jsonify({'error': 'CSV file is empty'}), 400
    except pd.errors.ParserError:
        print("Error parsing CSV file.")
        return jsonify({'error': 'Error parsing CSV file'}), 400
    except Exception as e:
        print(f"Error searching annotations: {e}")
        return jsonify({'error': str(e)}), 500

def init_app(app):
    app.register_blueprint(search_annotation_bp)
