import cv2
import torch
import pandas as pd
from torchvision import models
from torchvision.transforms import functional as F
from flask import jsonify
import os
from __init__ import temp_feature_data, SCORE_THRESHOLD, coco, upload_folder  # Adjust according to your app's structure


def process_image(image_path, filename):
    print(f"Processing image: {filename}")

    # Load the uploaded image
    image = cv2.imread(image_path)
    if image is None:
        return jsonify({'error': 'Could not read image'}), 400

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Load a pre-trained Faster R-CNN model
    model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.eval()

    # Transform the image for the model
    image_tensor = F.to_tensor(image_rgb).unsqueeze(0)

    # Perform object detection
    with torch.no_grad():
        outputs = model(image_tensor)

    # Store extracted features
    scores = outputs[0]['scores'].cpu().numpy()
    labels = outputs[0]['labels'].cpu().numpy()
    boxes = outputs[0]['boxes'].cpu().numpy()

    # Filter based on score threshold
    valid_indices = [i for i, score in enumerate(scores) if score >= SCORE_THRESHOLD]
    filtered_scores = scores[valid_indices]
    filtered_labels = [coco.cats[label]['name'] for label in labels[valid_indices]]
    filtered_boxes = boxes[valid_indices]

    # Save features to temp data
    temp_feature_data[filename] = {
        'scores': filtered_scores.tolist(),
        'labels': filtered_labels,
        'boxes': filtered_boxes.tolist()
    }

    # Create a temporary CSV file with the annotation positions
    df = pd.DataFrame({
        'score': filtered_scores,
        'label': filtered_labels,
        'box': [box.tolist() for box in filtered_boxes]
    })
    temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
    df.to_csv(temp_csv_path, index=False)
    print(f"CSV saved at: {temp_csv_path}")

    return jsonify({'message': 'Features extracted and saved temporarily.', 'ready_to_search': True})
