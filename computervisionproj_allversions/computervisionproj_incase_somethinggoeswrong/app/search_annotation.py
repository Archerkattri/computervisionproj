import os
import pandas as pd
import numpy as np
import cv2
from flask import jsonify
from __init__ import temp_feature_data, upload_folder  # Adjust according to your app's structure

def search_annotation(filename, query):
    print(f"Searching for '{query}' in {filename}")

    if filename not in temp_feature_data:
        return jsonify({'error': 'File not processed or data not available.'}), 400

    # Load CSV for the filename
    temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
    if not os.path.exists(temp_csv_path):
        print(f"CSV file not found: {temp_csv_path}")
        return jsonify({'error': 'CSV file not found'}), 404

    # Perform search in CSV
    try:
        df = pd.read_csv(temp_csv_path)
        print(f"Searching in CSV: {df}")

        matched_boxes = df[df['label'].str.contains(query, case=False)]
        print(f"Matched boxes after filtering: {matched_boxes}")

        if matched_boxes.empty:
            return jsonify({'error': f'The annotation "{query}" is not available in this file.'}), 404

        # Annotate the image or video
        is_video = filename.endswith(('.mp4', '.avi', '.mov'))
        annotated_image = None
        image_path = os.path.join(upload_folder, filename)

        if is_video:
            # Load the first frame for visualization
            video_capture = cv2.VideoCapture(image_path)
            ret, frame = video_capture.read()
            if not ret:
                return jsonify({'error': 'Could not read video frame.'}), 500
            annotated_image = frame
            video_capture.release()
        else:
            annotated_image = cv2.imread(image_path)
            if annotated_image is None:
                return jsonify({'error': 'Could not read image.'}), 500

        for index, row in matched_boxes.iterrows():
            box = np.array(eval(row['box'])).astype(int)
            cv2.rectangle(annotated_image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(annotated_image, row['label'], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1,
                        cv2.LINE_AA)

        annotated_image_filename = f'annotated_{filename}'
        annotated_image_path = os.path.join(upload_folder, annotated_image_filename)
        cv2.imwrite(annotated_image_path, annotated_image)
        print(f"Annotated image saved at: {annotated_image_path}")

        return jsonify({'annotated_file': f'/static/uploads/{annotated_image_filename}'}), 200

    except Exception as e:
        print(f"Error searching annotations: {e}")
        return jsonify({'error': 'Error occurred while searching annotations.'}), 500
