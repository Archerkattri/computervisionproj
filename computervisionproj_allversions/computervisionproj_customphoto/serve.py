import os
from flask import send_from_directory
from __init__ import app  # Import the Flask app

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/index.css')
def serve_css():
    return send_from_directory('src', 'index.css')

@app.route('/index.js')
def serve_js():
    return send_from_directory('src', 'index.js')

@app.route('/App.css')
def serve_app_css():
    return send_from_directory('src', 'App.css')

@app.route('/App.js')
def serve_app_js():
    return send_from_directory('src', 'App.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
