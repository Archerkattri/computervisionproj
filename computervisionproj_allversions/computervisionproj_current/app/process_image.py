import os
import logging
import time
import torch
import pandas as pd
from flask import Flask, jsonify, request
from PIL import Image
from pycocotools.coco import COCO
from .config import COCO_ANNOTATIONS_PATH, SCORE_THRESHOLD, upload_folder
from torchvision import models, transforms
from torchvision.models.detection import (
    ssdlite320_mobilenet_v3_large,
    FasterRCNN_ResNet50_FPN_Weights,
    KeypointRCNN_ResNet50_FPN_Weights,
    RetinaNet_ResNet50_FPN_Weights,
    SSDLite320_MobileNet_V3_Large_Weights,
    MaskRCNN_ResNet50_FPN_Weights
)
from typing import Dict, List, Tuple, Optional

# Define object detection models
models_dict = {
    'fasterrcnn': models.detection.fasterrcnn_resnet50_fpn(weights=FasterRCNN_ResNet50_FPN_Weights.COCO_V1),
    'keypointrcnn': models.detection.keypointrcnn_resnet50_fpn(weights=KeypointRCNN_ResNet50_FPN_Weights.COCO_V1),
    'retinanet': models.detection.retinanet_resnet50_fpn(weights=RetinaNet_ResNet50_FPN_Weights.COCO_V1),
    'ssdlite320': ssdlite320_mobilenet_v3_large(weights=SSDLite320_MobileNet_V3_Large_Weights.COCO_V1),
    'maskrcnn': models.detection.maskrcnn_resnet50_fpn(weights=MaskRCNN_ResNet50_FPN_Weights.COCO_V1),
}

# Initialize COCO API
coco = COCO(COCO_ANNOTATIONS_PATH)
coco_categories = coco.loadCats(coco.getCatIds())
category_id_to_name = {category['id']: category['name'] for category in coco_categories}

# Load models and set them to evaluation mode
for model_name, model_instance in models_dict.items():
    model_instance.eval()
    logging.info(f"{model_name} model loaded and set to evaluation mode.")

def detect_objects(model, image: Image.Image, image_name: str) -> Tuple[
    Optional[List[List[float]]], Optional[List[float]], Optional[List[str]]]:
    model_name = [name for name, instance in models_dict.items() if instance == model][0]
    logging.info(f"Starting detection with model: {model_name}")

    transform = transforms.ToTensor()
    image_tensor = transform(image).unsqueeze(0)

    try:
        with torch.no_grad():
            predictions = model(image_tensor)[0]  # Get the first result from the list

        if model_name in models_dict:
            # Access the predictions correctly
            boxes = predictions['boxes'].tolist()
            scores = predictions['scores'].tolist()
            labels = predictions['labels'].tolist()

            # Map label numbers to class names
            label_names = [category_id_to_name.get(int(label), 'Unknown') for label in labels]

            # Filter out low-confidence detections
            high_confidence_indices = [i for i, score in enumerate(scores) if score >= SCORE_THRESHOLD]
            boxes = [boxes[i] for i in high_confidence_indices]
            scores = [scores[i] for i in high_confidence_indices]
            label_names = [label_names[i] for i in high_confidence_indices]

            return boxes, scores, label_names

        else:
            logging.error(f"Model {model_name} is not recognized.")
            return None, None, None

    except Exception as e:
        logging.error(f"Error processing model {model_name}: {e}")
        return None, None, None

def process_model(model_name: str, image: Image.Image, image_name: str) -> Optional[Dict[str, any]]:
    logging.info(f"Processing model: {model_name} on file: {image_name}")

    model = models_dict.get(model_name)
    if not model:
        logging.error(f"Model {model_name} not found.")
        return None

    start_time = time.time()

    try:
        boxes, scores, label_names = detect_objects(model, image, image_name)

        csv_data = {
            'boxes': boxes,
            'scores': scores,
            'labels': label_names
        }
        csv_file_name = f'{model_name}_detections_{os.path.splitext(image_name)[0]}.csv'
        csv_path = os.path.join(upload_folder, csv_file_name)
        pd.DataFrame(csv_data).to_csv(csv_path, index=False)

        logging.info(f"Detection results saved to {csv_path}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        return {
            'file_name': csv_file_name,
            'metrics': {
                'inference_time': elapsed_time,
            },
        }

    except Exception as e:
        logging.error(f"Error processing model {model_name}: {e}")
        return None

def init_app(app: Flask) -> None:
    @app.route('/process-image', methods=['POST'])
    def process_image():
        app.logger.info('Processing image.')
        # Check if the request contains JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        image_name = data.get('image_name')

        # Validate image_name
        if not image_name:
            return jsonify({'error': 'Image name not provided'}), 400

        # Construct image file path
        image_path = os.path.join(upload_folder, image_name)

        if not os.path.isfile(image_path):
            return jsonify({'error': 'Image file does not exist'}), 404

        try:
            # Open the image file
            image = Image.open(image_path)
            file_name = image_name

            # Process each model
            all_results = {}
            for model_name, model_instance in models_dict.items():
                result = process_model(model_name, image, file_name)
                if result:
                    all_results[model_name] = result
            app.logger.info('Image processing complete.')
            return jsonify({'status': 'success', 'results': all_results})

        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return jsonify({'error': 'Error processing image'}), 500
