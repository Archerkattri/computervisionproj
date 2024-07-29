from flask import jsonify
from __init__ import coco

def get_coco_categories():
    try:
        # Load categories from COCO dataset
        categories = {cat['id']: cat['name'] for cat in coco.loadCats(coco.getCatIds())}
        return jsonify(categories), 200
    except Exception as e:
        print(f"Error fetching COCO categories: {e}")
        return jsonify({'error': 'An error occurred while fetching categories.'}), 500
