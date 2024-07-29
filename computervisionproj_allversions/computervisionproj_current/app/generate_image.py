import cv2
import os
import time
from flask import jsonify, request
from .config import upload_folder

def init_app(app):
    @app.route('/generate-image', methods=['POST'])
    def generate_image():
        data = request.json
        image_name = data.get('image_name')
        results = data.get('results')

        if not image_name or not results:
            return jsonify({'error': 'Missing image_name or results'}), 400

        image_path = os.path.join(upload_folder, image_name)
        print(f"Generating annotated images for: {image_name}")

        # Load the uploaded image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Could not read image'}), 400

        response = {'inference_results': []}

        for result in results:
            csv_filename = result.get('filename')
            bounding_boxes_data = result.get('boxes_data')

            # Derive model name from CSV filename
            model_name_with_ext = os.path.splitext(csv_filename)[0]
            model_name = model_name_with_ext
            if model_name.startswith('annotated_'):
                model_name = model_name[len('annotated_'):]
            # Remove the suffix _detections_<image_name>
            if '_detections_' in model_name:
                model_name = model_name.split('_detections_')[0]

            annotated_image = image.copy()

            start_time = time.time()

            if bounding_boxes_data:
                # Handle detection data
                for item in bounding_boxes_data:
                    box = item.get('boxes')
                    label = item.get('labels')

                    try:
                        # Convert string representation of list to list of ints
                        x1, y1, x2, y2 = map(int, eval(box))
                        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle with blue color
                        cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    except (ValueError, SyntaxError):
                        print(f"Invalid boxes format: {box}")
                        continue

            # Save the annotated image
            annotated_image_filename = f'annotated_{model_name}_{image_name}'
            annotated_image_path = os.path.join(upload_folder, annotated_image_filename)
            cv2.imwrite(annotated_image_path, annotated_image)
            print(f"Annotated image saved at: {annotated_image_path}")

            end_time = time.time()
            inference_time = end_time - start_time

            # Only include the file name in the response
            response['inference_results'].append({
                'annotated_image_name': annotated_image_filename,  # Return only the file name
                'inference_time': inference_time,
                'model_name': model_name
            })

        return jsonify(response), 200
