import cv2
import torch
import pandas as pd
from torchvision import models
from torchvision.transforms import functional as F
from flask import jsonify
import os
from __init__ import temp_feature_data, SCORE_THRESHOLD, coco, upload_folder  # Adjust according to your app's structure

def process_video(video_path, filename):
    print(f"Processing video: {filename}")
    model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.eval()

    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        return jsonify({'error': 'Could not open video'}), 400

    temp_feature_data[filename] = {'scores': [], 'labels': [], 'boxes': []}

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
        temp_feature_data[filename]['scores'].extend(filtered_scores.tolist())
        temp_feature_data[filename]['labels'].extend(filtered_labels)
        temp_feature_data[filename]['boxes'].extend(filtered_boxes.tolist())

    video_capture.release()
    print(f"Video processed and features saved temporarily.")

    # Save to CSV
    df = pd.DataFrame({
        'score': temp_feature_data[filename]['scores'],
        'label': temp_feature_data[filename]['labels'],
        'box': [box.tolist() for box in temp_feature_data[filename]['boxes']],
    })
    temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
    df.to_csv(temp_csv_path, index=False)
    print(f"CSV saved at: {temp_csv_path}")

    return jsonify({'message': 'Features extracted and saved temporarily.', 'ready_to_search': True})
