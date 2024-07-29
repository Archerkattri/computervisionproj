from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import cv2
import torch
import torchvision.models as models
from torchvision.transforms import functional as F
from werkzeug.utils import secure_filename
from pycocotools.coco import COCO
import shutil

app = Flask(__name__, static_folder='build', static_url_path='/')
socketio = SocketIO(app)

# Ensure the 'uploads' folder exists
upload_folder = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Initialize COCO API for instance annotations
dataDir = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory\Common_Objects_COCO'
dataType = 'val2017'
annFile = os.path.join(dataDir, 'annotations', f'instances_{dataType}.json')
imgDir = os.path.join(dataDir, dataType)
coco = COCO(annFile)

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
    print(f"Original {file_type} saved at: {file_path}")

    if file_type == 'image':
        return process_image(file_path)
    elif file_type == 'video':
        return process_video(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'})

def process_image(image_path):
    # Load the uploaded image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Load a pre-trained Faster R-CNN model with recommended weights parameter
    model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.eval()

    # Transform the image for the model
    image_tensor = F.to_tensor(image_rgb).unsqueeze(0)

    # Perform object detection
    with torch.no_grad():
        outputs = model(image_tensor)

    # Display the results
    scores = outputs[0]['scores'].cpu().numpy()
    labels = outputs[0]['labels'].cpu().numpy()
    boxes = outputs[0]['boxes'].cpu().numpy()

    # Filter out weak detections
    threshold = 0.8
    filtered_boxes = boxes[scores > threshold].astype(int)

    # Annotate image with bounding boxes and labels
    for box, label in zip(filtered_boxes, labels):
        cv2.rectangle(image_rgb, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        category_id = int(label)
        category_name = coco.cats[category_id]['name']
        cv2.putText(image_rgb, category_name, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    # Save the annotated image
    annotated_image_filename = 'annotated_' + os.path.basename(image_path)
    annotated_image_path = os.path.join(upload_folder, annotated_image_filename)
    cv2.imwrite(annotated_image_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    print(f"Annotated image saved at: {annotated_image_path}")

    return jsonify({
        'original_file': f'/static/uploads/{os.path.basename(image_path)}',
        'annotated_file': f'/static/uploads/{annotated_image_filename}'
    })

def process_video(video_path):
    # Load a pre-trained Faster R-CNN model with recommended weights parameter
    model = models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.eval()

    # Open the video file
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        return jsonify({'error': 'Could not open video'})

    # Get video properties
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Use mp4v codec
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    # Prepare to save the annotated video
    annotated_video_filename = 'annotated_' + os.path.basename(video_path)
    annotated_video_path = os.path.join(upload_folder, annotated_video_filename)
    video_writer = cv2.VideoWriter(annotated_video_path, codec, fps, (width, height))

    frame_number = 0
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_tensor = F.to_tensor(frame_rgb).unsqueeze(0)

        # Perform object detection
        with torch.no_grad():
            outputs = model(frame_tensor)

        # Display the results
        scores = outputs[0]['scores'].cpu().numpy()
        labels = outputs[0]['labels'].cpu().numpy()
        boxes = outputs[0]['boxes'].cpu().numpy()

        # Filter out weak detections
        threshold = 0.8
        filtered_boxes = boxes[scores > threshold].astype(int)

        # Annotate frame with bounding boxes and labels
        for box, label in zip(filtered_boxes, labels):
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            category_id = int(label)
            category_name = coco.cats[category_id]['name']
            cv2.putText(frame, category_name, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

        video_writer.write(frame)
        frame_number += 1

    video_capture.release()
    video_writer.release()
    print(f"Annotated video saved at: {annotated_video_path}")

    return jsonify({
        'original_file': f'/static/uploads/{os.path.basename(video_path)}',
        'annotated_file': f'/static/uploads/{annotated_video_filename}'
    })

@app.route('/clear', methods=['POST'])
def clear():
    # Clear all files in the upload folder
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    return jsonify({'message': 'Files cleared successfully'})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/uploads/<path:filename>')
def serve_files(filename):
    return send_from_directory(upload_folder, filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)