from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import os
import cv2
import torch
import torchvision.models as models
from torchvision.transforms import functional as F
from werkzeug.utils import secure_filename
from pycocotools.coco import COCO
import pandas as pd
import numpy as np

app = Flask(__name__, static_folder='build', static_url_path='/')
socketio = SocketIO(app)

# Ensure the 'uploads' folder exists
upload_folder = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Initialize COCO API for instance annotations
dataDir = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO'
dataType = 'val2017'
annFile = os.path.join(dataDir, 'annotations', f'instances_{dataType}.json')
coco = COCO(annFile)

# Store temporary feature data
temp_feature_data = {}

# Score threshold
SCORE_THRESHOLD = 0.8

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file_type = request.form.get('file_type', 'image')

    # Save uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    print(f"Received {file_type}: {filename} saved at: {file_path}")

    if file_type == 'image':
        return process_image(file_path, filename)
    elif file_type == 'video':
        return process_video(file_path, filename)
    else:
        return jsonify({'error': 'Unsupported file type'})

def process_image(image_path, filename):
    print(f"Processing image: {filename}")

    # Load the uploaded image
    image = cv2.imread(image_path)
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
    print(f"CSV content:\n{df}")

    return jsonify({'message': 'Features extracted and saved temporarily.', 'ready_to_search': True})

def process_video(video_path, filename):
    print(f"Processing video: {filename}")
    model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.eval()

    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        return jsonify({'error': 'Could not open video'})

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
    print(f"CSV content:\n{df}")

    return jsonify({'message': 'Features extracted and saved temporarily.', 'ready_to_search': True})

@app.route('/search', methods=['POST'])
def search_annotation():
    data = request.json
    filename = data.get('filename')
    query = data.get('query').strip()  # Normalize query

    print(f"Searching for '{query}' in {filename}")

    if filename not in temp_feature_data:
        return jsonify({'error': 'File not processed or data not available.'})

    # Load CSV for the filename
    temp_csv_path = os.path.join(upload_folder, f'{filename}.csv')
    if not os.path.exists(temp_csv_path):
        print(f"CSV file not found: {temp_csv_path}")
        return jsonify({'error': 'CSV file not found'})

    # Perform search in CSV
    try:
        df = pd.read_csv(temp_csv_path)
        print(f"Searching in CSV: {df}")  # Debugging line

        matched_boxes = df[df['label'].str.contains(query, case=False)]
        print(f"Matched boxes after filtering: {matched_boxes}")  # Debugging line

        if matched_boxes.empty:
            return jsonify({'error': f'The annotation "{query}" is not available in this file.'})

        # Print the box data for matched labels
        for index, row in matched_boxes.iterrows():
            print(f"Matched label: {row['label']}, Box data: {eval(row['box'])}")

        # Annotate the image or video
        is_video = filename.endswith(('.mp4', '.avi', '.mov'))
        annotated_image = None
        image_path = os.path.join(upload_folder, filename)

        if is_video:
            # Load the first frame for visualization
            video_capture = cv2.VideoCapture(image_path)
            ret, frame = video_capture.read()
            if not ret:
                return jsonify({'error': 'Could not read video frame.'})
            annotated_image = frame
            video_capture.release()
        else:
            annotated_image = cv2.imread(image_path)

        for index, row in matched_boxes.iterrows():
            box = np.array(eval(row['box'])).astype(int)  # Convert string to numpy array
            cv2.rectangle(annotated_image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(annotated_image, row['label'], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1,
                        cv2.LINE_AA)

        annotated_image_filename = 'annotated_' + filename
        annotated_image_path = os.path.join(upload_folder, annotated_image_filename)
        cv2.imwrite(annotated_image_path, annotated_image)
        print(f"Annotated image saved at: {annotated_image_path}")

        return jsonify({'annotated_file': f'/static/uploads/{annotated_image_filename}'})

    except Exception as e:
        print(f"Error searching annotations: {e}")
        return jsonify({'error': 'Error occurred while searching annotations.'})

@app.route('/clear', methods=['POST'])
def clear():
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    print("All files cleared successfully.")
    return jsonify({'message': 'Files cleared successfully'})

@app.route('/coco-categories', methods=['GET'])
def get_coco_categories():
    categories = {cat['id']: cat['name'] for cat in coco.loadCats(coco.getCatIds())}
    return jsonify(categories)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
