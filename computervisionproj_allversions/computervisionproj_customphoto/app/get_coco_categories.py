from flask import jsonify
from .config import coco  # Ensure coco is properly imported

def get_coco_categories():
    categories = {cat['id']: cat['name'] for cat in coco.loadCats(coco.getCatIds())}
    return categories  # Return the categories dictionary directly

def init_app(app):
    @app.route('/coco_categories', methods=['GET'])
    def fetch_coco_categories():
        return jsonify(get_coco_categories()), 200
