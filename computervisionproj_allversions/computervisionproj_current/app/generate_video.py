import cv2
import os
import json
from flask import jsonify, request
from .config import upload_folder

def init_app(app):
    @app.route('/generate-video', methods=['POST'])
    def generate_video():
        data = request.json
        video_name = data.get('video_name')  # Changed to 'video_name' to match payload
        annotations = data.get('annotations')

        if not video_name or not isinstance(annotations, list) or not all(
                isinstance(annotation, dict) for annotation in annotations):
            return jsonify(
                {'error': 'Missing video_name or annotations, or annotations are not in the correct format'}), 400

        video_path = os.path.join(upload_folder, video_name)

        print(f"Generating annotated video for: {os.path.basename(video_path)}")

        # Load the uploaded video
        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            return jsonify({'error': 'Could not open video'}), 400

        # Get video properties
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        annotated_video_filename = f'annotated_{video_name}'
        annotated_video_path = os.path.join(upload_folder, annotated_video_filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(annotated_video_path, fourcc, fps, (width, height))

        # Create a dictionary for easy lookup of annotations by frame number
        annotations_by_frame = {}
        for annotation in annotations:
            frame_number = annotation['frame']
            if frame_number not in annotations_by_frame:
                annotations_by_frame[frame_number] = []
            annotations_by_frame[frame_number].append(annotation['bounding_boxes'])

        # Process video frames
        frame_index = 0
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break

            # Annotate the frame with bounding boxes
            if frame_index in annotations_by_frame:
                for box in annotations_by_frame[frame_index]:
                    # Ensure box is a list of floats
                    if not isinstance(box, list) or len(box) != 4:
                        return jsonify({'error': 'Bounding box must be a list with four elements'}), 400

                    try:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle with blue color
                    except ValueError:
                        return jsonify({'error': 'Bounding box contains non-numeric values'}), 400

            out.write(frame)
            frame_index += 1

        video_capture.release()
        out.release()
        print(f"Annotated video saved at: {annotated_video_path}")

        # Return a relative path that Flask can serve
        relative_video_path = os.path.join('uploads', annotated_video_filename)
        return jsonify(
            {'message': 'Annotated video generated successfully.', 'annotated_video_path': relative_video_path})
