import os
from flask import send_from_directory
from werkzeug.utils import safe_join
from __init__ import app

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "":
        try:
            safe_path = safe_join(app.static_folder, path)
        except Exception:
            safe_path = None
        if safe_path is not None and os.path.exists(safe_path):
            return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
