# config.py
import os
from pycocotools.coco import COCO

# Ensure the 'uploads' folder exists
upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Initialize COCO API for instance annotations
dataDir = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO'
dataType = 'val2017'
annFile = os.path.join(dataDir, 'annotations', f'instances_{dataType}.json')
coco = COCO(annFile)

# Score threshold
SCORE_THRESHOLD = 0.8
