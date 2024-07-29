import cv2
import os
import pandas as pd
import torch
from torchvision import models, transforms
from flask import jsonify, request
from .config import upload_folder
from .get_coco_categories import get_coco_categories

# Load the pre-trained Faster R-CNN model
model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

def detect_objects(image):
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        predictions = model(image_tensor)

    boxes = []
    scores = []
    labels = []

    for box, score, label in zip(predictions[0]['boxes'], predictions[0]['scores'], predictions[0]['labels']):
        if score > 0.8:
            boxes.append(box.tolist())
            scores.append(score.item())
            labels.append(label.item())

    return boxes, scores, labels

def init_app(app):
    @app.route('/process-image', methods=['POST'])
    def process_image():
        data = request.json  # Make sure the client sends JSON data
        print(data)  # Log incoming data for debugging

        file_name = data.get('file_name')  # Expecting 'file_name' instead of 'file_path'
        if not file_name:
            return jsonify({'error': 'Missing file_name'}), 400

        image_path = os.path.join(upload_folder, file_name)
        print(f"Processing image: {os.path.basename(image_path)}")

        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Could not read image'}), 400

        boxes, scores, labels = detect_objects(image)

        coco_categories = get_coco_categories()

        data_to_save = []
        label_names = {label_id: label_name for label_id, label_name in coco_categories.items()}

        for box, score, label in zip(boxes, scores, labels):
            label_name = label_names[label]
            data_to_save.append({
                'label': label_name,
                'bounding_boxes': box,
                'score': score
            })

        csv_file_name = f'detections_{os.path.basename(file_name).split(".")[0]}.csv'
        csv_path = os.path.join(upload_folder, csv_file_name)
        df = pd.DataFrame(data_to_save)

        try:
            df.to_csv(csv_path, index=False)
            print(f"CSV file saved at: {csv_path}")
        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")
            return jsonify({'error': 'Failed to save CSV file'}), 500

        # Return the CSV path for further processing
        return jsonify({'csv_file_name': csv_file_name})
