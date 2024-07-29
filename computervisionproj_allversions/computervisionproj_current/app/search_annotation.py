import os
import pandas as pd
from flask import Blueprint, jsonify, request
from .config import upload_folder

search_annotation_bp = Blueprint('search_annotation', __name__)

@search_annotation_bp.route('/search', methods=['POST'])
def search_annotation():
    data = request.json
    csv_file_names = data.get('csv_file_names', [])
    query = data.get('query')

    if not csv_file_names or not query:
        return jsonify({'error': 'No csv_file_names or query provided'}), 400

    labels_results = []

    for csv_file_name in csv_file_names:
        # Load CSV for the filename
        temp_csv_path = os.path.join(upload_folder, csv_file_name)
        if not os.path.exists(temp_csv_path):
            print(f"CSV file not found: {temp_csv_path}")
            continue

        try:
            # Read CSV and filter based on query
            df = pd.read_csv(temp_csv_path)

            if 'labels' in df.columns:
                # Detection file: Extract boxes from 'labels'
                matched_entries = df[df['labels'].str.contains(query, case=False, na=False)]
                if not matched_entries.empty:
                    boxes_data = matched_entries[['labels', 'boxes']].to_dict(orient='records')
                    labels_results.append({
                        'filename': csv_file_name,
                        'boxes_data': boxes_data
                    })

        except pd.errors.EmptyDataError:
            print(f"CSV file is empty: {temp_csv_path}")
            continue
        except pd.errors.ParserError:
            print(f"Error parsing CSV file: {temp_csv_path}")
            continue
        except Exception as e:
            print(f"Error searching annotations in {csv_file_name}: {e}")
            continue

    if not labels_results:
        return jsonify({'error': f'The annotation "{query}" is not available in the provided files.'}), 404

    return jsonify({'results': labels_results}), 200

def init_app(app):
    app.register_blueprint(search_annotation_bp)
