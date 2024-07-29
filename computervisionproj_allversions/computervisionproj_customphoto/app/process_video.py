import cv2
import torch
import pandas as pd
from torchvision import models
from torchvision.transforms import functional as F
from flask import jsonify, request
import os
from .config import upload_folder, SCORE_THRESHOLD, coco

def init_app(app):
    @app.route('/process-video', methods=['POST'])
    def process_video():
        video_path = request.json['video_path']  # Get video path from request
        filename = os.path.basename(video_path)

        print(f"Processing video: {filename}")

        # Load a pre-trained Faster R-CNN model
        model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
        model.eval()

        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            return jsonify({'error': 'Could not open video'}), 400

        # Initialize lists to store features
        scores_list = []
        labels_list = []
        boxes_list = []

        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_tensor = F.to_tensor(frame_rgb).unsqueeze(0)

            with torch.no_grad():
                outputs = model(frame_tensor)

            scores = outputs[0]['scores'].cpu().numpy()
            labels = outputs[0]['labels'].cpu().numpy()
            boxes = outputs[0]['boxes'].cpu().numpy()

            # Filter based on score threshold
            valid_indices = [i for i, score in enumerate(scores) if score >= SCORE_THRESHOLD]
            filtered_scores = scores[valid_indices]
            filtered_labels = [coco.cats[label]['name'] for label in labels[valid_indices]]
            filtered_boxes = boxes[valid_indices]

            # Store features
            scores_list.extend(filtered_scores.tolist())
            labels_list.extend(filtered_labels)
            boxes_list.extend(filtered_boxes.tolist())

        video_capture.release()
        print(f"Video processed and features saved temporarily.")

        # Save to CSV
        df = pd.DataFrame({
            'score': scores_list,
            'label': labels_list,
            'box': [box.tolist() for box in boxes_list],
        })
        temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
        df.to_csv(temp_csv_path, index=False)
        print(f"CSV saved at: {temp_csv_path}")

        return jsonify({'message': 'Features extracted and saved temporarily.', 'ready_to_search': True})
