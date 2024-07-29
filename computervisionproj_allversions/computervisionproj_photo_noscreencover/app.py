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
import time

app = Flask(__name__, static_folder='build', static_url_path='/')
socketio = SocketIO(app)

# Ensure the 'images' folder exists
image_upload_folder = os.path.join(app.root_path, 'static', 'images')
os.makedirs(image_upload_folder, exist_ok=True)

# Initialize COCO API for instance annotations
dataDir = r'C:\Users\krish\Documents\Project\FeatureRecall\impfiles\DataDirectory'
dataType = 'val2017'
annFile = os.path.join(dataDir, 'annotations', f'instances_{dataType}.json')
imgDir = os.path.join(dataDir, dataType)
coco = COCO(annFile)

@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save uploaded file
    image_filename = secure_filename(file.filename)
    image_path = os.path.join(image_upload_folder, image_filename)
    file.save(image_path)
    print(f"Original image saved at: {image_path}")

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
    annotated_image_filename = 'annotated_' + image_filename
    annotated_image_path = os.path.join(image_upload_folder, annotated_image_filename)
    cv2.imwrite(annotated_image_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    print(f"Annotated image saved at: {annotated_image_path}")

    return jsonify({
        'annotated_image': f'/static/images/{annotated_image_filename}'
    })

@app.route('/clear', methods=['POST'])
def clear():
    # Clear all files in the image upload folder
    for filename in os.listdir(image_upload_folder):
        file_path = os.path.join(image_upload_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    return jsonify({'message': 'Images cleared successfully'})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(image_upload_folder, filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)