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

def detect_objects(frame):
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    frame_tensor = transform(frame).unsqueeze(0)

    with torch.no_grad():
        predictions = model(frame_tensor)

    boxes = []
    scores = []
    labels = []

    for box, score, label in zip(predictions[0]['boxes'], predictions[0]['scores'], predictions[0]['labels']):
        if score > 0.8:  # Adjust the threshold as needed
            boxes.append(box.tolist())
            scores.append(score.item())
            labels.append(label.item())

    return boxes, scores, labels

def init_app(app):
    @app.route('/process-video', methods=['POST'])
    def process_video():
        data = request.json
        print(data)  # Log incoming data for debugging

        file_name = data.get('file_name')  # Expecting 'file_name' instead of 'video_path'
        if not file_name:
            return jsonify({'error': 'Missing file_name'}), 400

        video_path = os.path.join(upload_folder, file_name)
        print(f"Processing video: {os.path.basename(video_path)}")

        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            return jsonify({'error': 'Could not open video'}), 400

        coco_categories = get_coco_categories()
        label_names = {label_id: label_name for label_id, label_name in coco_categories.items()}

        data_to_save = []

        frame_number = 0
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_number += 1
            timestamp = video_capture.get(cv2.CAP_PROP_POS_MSEC)  # Get timestamp in milliseconds

            boxes, scores, labels = detect_objects(frame)

            for box, score, label in zip(boxes, scores, labels):
                label_name = label_names[label]
                data_to_save.append({
                    'timestamp': timestamp,
                    'frame': frame_number,
                    'label': label_name,
                    'bounding_boxes': box,
                    'score': score
                })

        video_capture.release()
        print(f"Video processed: {file_name}")

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
