import cv2
import os
from flask import jsonify, request
from .config import upload_folder

def init_app(app):
    @app.route('/generate-image', methods=['POST'])
    def generate_image():
        data = request.json
        image_path = data.get('image_path')
        boxes = data.get('boxes')

        if not image_path or not isinstance(boxes, list) or not all(isinstance(box, list) and len(box) == 4 for box in boxes):
            return jsonify({'error': 'Missing image_path or boxes, or boxes are not in the correct format'}), 400

        print(f"Generating annotated image for: {os.path.basename(image_path)}")

        # Load the uploaded image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Could not read image'}), 400

        # Annotate the image with bounding boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle with blue color

        # Save the annotated image
        annotated_image_filename = f'annotated_{os.path.basename(image_path)}'
        annotated_image_path = os.path.join(upload_folder, annotated_image_filename)
        cv2.imwrite(annotated_image_path, image)
        print(f"Annotated image saved at: {annotated_image_path}")

        # Return a relative path that Flask can serve
        relative_image_path = os.path.join('uploads', annotated_image_filename)
        return jsonify({'message': 'Annotated image generated successfully.', 'annotated_image_path': relative_image_path})
