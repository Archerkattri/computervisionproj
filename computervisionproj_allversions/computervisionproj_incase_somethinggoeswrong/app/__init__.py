from flask import Flask
from flask_socketio import SocketIO
import os
from pycocotools.coco import COCO

app = Flask(__name__, static_folder='build', static_url_path='/')
socketio = SocketIO(app)

# Ensure the 'uploads' folder exists
upload_folder = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Score threshold
SCORE_THRESHOLD = 0.8

# Initialize COCO API for instance annotations
dataDir = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO'
dataType = 'val2017'
annFile = os.path.join(dataDir, 'annotations', f'instances_{dataType}.json')
coco = COCO(annFile)

# Store temporary feature data
temp_feature_data = {}

# Import the routes from other modules
from process_file import *
from process_image import *
from process_video import *
from search_annotation import *
from clear import *
from get_coco_categories import *
from serve import *

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
