import requests
import random

# Configuration
base_url = 'http://localhost:5000'  # Replace with your Flask server URL
process_image_endpoint = '/process-image'
fetch_annotations_endpoint = '/fetch-annotations'
search_endpoint = '/search'
generate_image_endpoint = '/generate-image'
image_name = 'WhatsApp Image 2024-07-11 at 01.22.43_e56a204c.jpg'  # Replace with your image file name


# Step 1: Process the image to generate CSV files
def process_image(image_name):
    process_image_data = {
        'image_name': image_name  # Pass the file name to process-image
    }
    response = requests.post(f'{base_url}{process_image_endpoint}', json=process_image_data)
    if response.status_code == 200:
        return response.json()  # Expecting response to include CSV file names and performance metrics
    else:
        print('Failed to process image:', response.text)
        return None


# Step 2: Fetch unique annotations
def fetch_annotations(csv_file_names):
    fetch_annotations_data = {
        'csv_file_names': csv_file_names
    }
    response = requests.post(f'{base_url}{fetch_annotations_endpoint}', json=fetch_annotations_data)
    if response.status_code == 200:
        return response.json()  # Expecting response to include unique labels
    else:
        print('Failed to fetch annotations:', response.text)
        return None


# Step 3: Search for the label and generate annotated image
def search_and_generate_image(csv_file_names, query):
    search_data = {
        'csv_file_names': csv_file_names,
        'query': query
    }
    response = requests.post(f'{base_url}{search_endpoint}', json=search_data)
    if response.status_code == 200:
        search_results = response.json()
        # Generate the annotated image based on search results
        generate_data = {
            'image_name': image_name,
            'results': search_results.get('results', [])
        }
        response = requests.post(f'{base_url}{generate_image_endpoint}', json=generate_data)
        if response.status_code == 200:
            print('Annotated image generated successfully.')
        else:
            print('Failed to generate annotated image:', response.text)
    else:
        print('Failed to search annotations:', response.text)


# Main function to run the test
def main():
    # Step 1: Process the image
    result = process_image(image_name)
    if result:
        # Extract CSV file names from result
        results = result.get('results', {})
        csv_file_names = [model_result['file_name'] for model_result in results.values()]

        # Step 2: Fetch annotations from the generated CSV files
        annotations = fetch_annotations(csv_file_names)
        if annotations:
            # Assuming 'annotations' contains a key 'labels' or similar
            labels = annotations.get('labels', [])
            if labels:
                # Step 3: Search for a label and generate annotated image
                search_and_generate_image(csv_file_names, random.choice(labels))


if __name__ == '__main__':
    main()
