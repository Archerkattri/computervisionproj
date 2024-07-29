# config.py
import os
from pycocotools.coco import COCO

# Ensure the 'uploads' folder exists
upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Paths for COCO data
COCO_ANNOTATIONS_PATH = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO\annotations\instances_val2017.json'
COCO_IMAGES_PATH = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO\val2017'

# Initialize COCO API for instance annotations
coco = COCO(COCO_ANNOTATIONS_PATH)

# Score threshold
SCORE_THRESHOLD = 0.8
