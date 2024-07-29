# Computer Vision Project: React and Flask Application

## Overview

This project is a React and Flask-based application that allows users to upload images or videos, process them using various computer vision models, and view annotated results. The project has evolved through several versions, each adding new features, optimizations, and improvements.

## Project Versions

### 1. `computervisionproj_photo_noscreencover`
- **Objective**: Initial implementation focusing on photo processing.
- **Features**: Utilized Faster R-CNN for annotating images.
- **UI**: Basic React web app for uploading photos and viewing results.
- **Notes**: This was the first successful implementation after resolving an issue with images covering the screen. The project only processed photos at this stage.Change the path(s) according to your needs in this and all future versions.

### 2. `computervisionproj_photo_scrollandborder`
- **Objective**: Improved handling of images with different aspect ratios and sizes.
- **Features**: Enabled scrolling and added borders to the image display area for consistent presentation.
- **Skills Improved**: Computer vision, React, and Flask.

### 3. `computervisionproj_video`
- **Objective**: Extended the functionality to process videos.
- **Features**: Similar to the photo version but included video processing using Faster R-CNN.

### 4. `computervisionproj_incase_somethinggoeswrong`
- **Objective**: Code optimization and modularization.
- **Features**: 
  - Split the code into modular Python files for better organization and maintainability.
  - Introduced CSV generation before creating annotated images or videos, allowing for more control over the annotations.

### 5. `computervisionproj_customphoto`
- **Objective**: Further optimizations and improved UI.
- **Features**: 
  - Added buttons for labels, enabling easy selection and generation of annotated images.
  - Implemented logging via `init.log` to track application activities.
  - Video feature was disabled in this version.

### 6. `computervisionproj_customvideo`
- **Objective**: Enabled video processing alongside photo processing.
- **Features**: Similar to `computervisionproj_customphoto` but with a functioning video feature.

### 7. `computervisionproj_current`
- **Objective**: Comprehensive model testing and comparison.
- **Features**: 
  - Tested multiple models including Faster R-CNN, Keypoint R-CNN, Mask R-CNN, RetinaNet, and SSDlite.
  - Observations:
    - **Mask R-CNN**: Provided the most annotations with a confidence score above 0.8 and was relatively fast.
    - **SSDlite**: Fastest model but with the fewest annotations/labels.
    - **RetinaNet & Keypoint R-CNN**: Similar performance in terms of labels and speed, but Keypoint R-CNN had a better confidence score.
    - **Faster R-CNN**: Second best after Mask R-CNN, offering a good balance of speed and annotation quality.

### 8. Upcoming Version: `computervisionproj_focus_auto_population_scan`
- **Objective**: Development of a custom model called "Focus Auto-Population Scan".
- **Status**: Work in progress, not yet uploaded to GitHub.

## Running the Application

1. **Clone the Repository**: Clone the repository from GitHub to your local machine.
2. **Install Dependencies**: Use `npm install` for React dependencies and `pip install -r requirements.txt` for Python dependencies.
3. **Start the Flask Backend**:
   - Navigate to the `app` directory: `cd app`.
   - Set `__init__.py` as the Flask app: `export FLASK_APP=__init__.py` (use `set` instead of `export` if you're on Windows).
   - Run the Flask server: `flask run`.
4. **Build the React Frontend**:
   - In a separate terminal, navigate to the project directory.
   - Run `npm run build` to build the React application.
5. **Upload Images/Videos**: Use the web interface to upload files and view the annotated results.

## Contributions and Feedback

Contributions are welcome. Please fork the repository and submit a pull request. For any issues or feedback, open an issue on GitHub.

## Future Plans

- Integration of the "Focus Auto-Population Scan" model.
- Further optimization and enhancement of the UI/UX.
- Expansion of the model library for better comparison and feature set.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.