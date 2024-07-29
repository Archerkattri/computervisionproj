import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [selectedType, setSelectedType] = useState(null); // 'image' or 'video'
  const [originalFileUrl, setOriginalFileUrl] = useState(null);
  const [annotations, setAnnotations] = useState([]);
  const [csvFileNames, setCsvFileNames] = useState([]); // State to store CSV file names
  const [annotatedImages, setAnnotatedImages] = useState([]); // State to store annotated images per model
  const [currentStep, setCurrentStep] = useState(''); // Track the current step

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    console.debug('File selected: ' + selectedFile.name);
    setFile(selectedFile);
    setOriginalFileUrl(URL.createObjectURL(selectedFile));
    setAnnotatedImages([]); // Clear annotated images
    setAnnotations([]);
    setCsvFileNames([]);
    setCurrentStep('File selected'); // Update step
  };

  const handleUpload = async () => {
    if (!file || !selectedType) return;

    setCurrentStep('Uploading...'); // Update step
    console.debug('Uploading ' + selectedType + ': ' + file.name);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.debug('Upload Response: ' + JSON.stringify(uploadResponse.data));

      const csvFiles = uploadResponse.data.csv_files;
      if (!csvFiles) {
        throw new Error('csv_files not found in response');
      }

      const csvFileNames = Object.values(csvFiles).map(result => result.file_name);
      if (!csvFileNames.length) {
        throw new Error('No CSV file names found');
      }

      setCsvFileNames(csvFileNames); // Save CSV file names for later use

      setCurrentStep('Fetching annotations...'); // Update step
      const annotationsResponse = await axios.post('http://localhost:5000/fetch-annotations', {
        csv_file_names: csvFileNames
      });
      console.debug('Annotations Response: ' + JSON.stringify(annotationsResponse.data));
      setAnnotations(annotationsResponse.data.labels);
      setCurrentStep('Annotations fetched'); // Update step

      // Dynamically create spaces for annotated images based on model names
      const modelNames = Object.keys(csvFiles); // Use keys from csvFiles to get model names
      setAnnotatedImages(modelNames.map(modelName => ({
        modelName,
        imageUrl: null,
        inferenceTime: null
      })));

    } catch (error) {
      console.error('Error uploading ' + selectedType + ':', error);
      setCurrentStep('Error during upload'); // Update step
    }
  };

  const handleClear = () => {
    console.debug('Clearing all fields');
    setFile(null);
    setSelectedType(null);
    setOriginalFileUrl(null);
    setAnnotatedImages([]); // Clear annotated images
    setAnnotations([]);
    setCsvFileNames([]);
    setCurrentStep(''); // Reset step
  };

const handleAnnotationClick = async (annotation) => {
  console.log('Annotation clicked:', annotation);

  try {
    setCurrentStep('Searching annotation...');

    // Step 1: Search annotations
    const searchResponse = await axios.post('http://localhost:5000/search', {
      csv_file_names: csvFileNames,
      query: annotation // Ensure payload structure matches the backend's expectations
    });
    console.debug('Search Response:', searchResponse.data);

    if (!searchResponse.data || !searchResponse.data.results) {
      throw new Error('No results found in search response');
    }

    const results = searchResponse.data.results;

    if (selectedType === 'image') {
      const allBoxes = results.flatMap(result =>
        result.boxes_data.map(boxData => ({
          ...JSON.parse(boxData.boxes),
          label: boxData.labels
        }))
      );

      setAnnotatedImages(prevImages =>
        prevImages.map(image => ({
          ...image,
          imageUrl: null,
          inferenceTime: null
        }))
      );

      setCurrentStep('Generating annotated images...');

      const generateImagePromises = annotatedImages.map(async (image) => {
        console.debug('Generating image for:', image.modelName);
        console.debug('Image Name:', file.name);
        console.debug('Results:', results);

        const generateImageResponse = await axios.post('http://localhost:5000/generate-image', {
          image_name: file.name,
          results: results
        });

        console.debug('Generate Image Response:', generateImageResponse.data);

        if (!generateImageResponse.data || !generateImageResponse.data.inference_results) {
          throw new Error('Annotated image name is missing in the response');
        }

        const annotatedImageNames = generateImageResponse.data.inference_results.map(result => result.annotated_image_name);

        const uniqueId = new Date().getTime();
        return annotatedImageNames.map(name => ({
          modelName: image.modelName,
          imageUrl: `http://localhost:5000/uploads/${name}?${uniqueId}`,
          inferenceTime: generateImageResponse.data.inference_time
        }));
      });

      const annotatedImagesData = (await Promise.all(generateImagePromises)).flat();
      setAnnotatedImages(annotatedImagesData);
      setCurrentStep('Annotated images generated');

    } else if (selectedType === 'video') {
      const allAnnotations = results.flatMap(result =>
        result.boxes_data.map(boxData => ({
          bounding_boxes: JSON.parse(boxData.boxes),
          label: boxData.labels
        }))
      );

      setAnnotatedImages([]);
      setCurrentStep('Generating annotated video...');

      const generateVideoResponse = await axios.post('http://localhost:5000/generate-video', {
        video_name: file.name,
        annotations: allAnnotations
      });
      console.debug('Generate Video Response:', generateVideoResponse.data);

      if (!generateVideoResponse.data || !generateVideoResponse.data.annotated_video_path) {
        throw new Error('Annotated video path is missing in the response');
      }

      const uniqueId = new Date().getTime();
      const videoUrl = `http://localhost:5000/${generateVideoResponse.data.annotated_video_path}?${uniqueId}`;
      console.debug('Annotated Video URL:', videoUrl);

      setAnnotatedImages([{ modelName: 'Annotated Video', imageUrl: videoUrl, inferenceTime: null }]);
      setCurrentStep('Annotated video generated');
    }
  } catch (error) {
    console.error('Error searching annotation:', error);
    if (error.response) {
      console.error('Response error:', error.response.data);
    }
    setCurrentStep('Error searching annotation');
  }
};

  return (
    <div className='App'>
      <header className='App-header'>
        <h1>Searchable Visual Result App</h1>
        <div>
          <button onClick={() => setSelectedType('image')} disabled={selectedType === 'image'}>
            Process Image
          </button>
          <button onClick={() => setSelectedType('video')} disabled={selectedType === 'video'}>
            Process Video
          </button>
        </div>
        {selectedType && (
          <>
            <label>
              Choose File:
              <input type='file' accept={selectedType === 'image' ? 'image/*' : 'video/*'} onChange={handleFileChange} />
            </label>
            <button onClick={handleUpload} disabled={!file}>
              Upload and Process
            </button>
            <button onClick={handleClear}>Clear</button>
            <div className='current-step'>
              <h3>Current Step:</h3>
              <p>{currentStep || 'No step in progress'}</p>
            </div>
            <div>
              {annotations.length > 0 && (
                <div>
                  <h3>Available Annotations:</h3>
                  <div className='annotation-buttons'>
                    {annotations.map((annotation, index) => (
                      <button key={index} onClick={() => handleAnnotationClick(annotation)}>
                        {annotation}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className='media-container'>
              <div className='media-box'>
                <h2>Original {selectedType === 'image' ? 'Image' : 'Video'}</h2>
                {originalFileUrl ? (
                  selectedType === 'image' ? (
                    <img src={originalFileUrl} alt='Original' className='preview' />
                  ) : (
                    <video src={originalFileUrl} controls className='preview' />
                  )
                ) : (
                  <div className='placeholder'>No {selectedType} selected</div>
                )}
              </div>
              <div className='media-box'>
                <h2>Annotated {selectedType === 'image' ? 'Images' : 'Video'}</h2>
                {annotatedImages.length > 0 ? (
                  selectedType === 'image' ? (
                    annotatedImages.map((image, index) => (
                      <div key={index}>
                        <h3>{image.modelName}</h3>
                        <img src={image.imageUrl} alt={image.modelName} className='preview' />
                        {image.inferenceTime && <p>Inference Time: {image.inferenceTime} ms</p>}
                      </div>
                    ))
                  ) : (
                    annotatedImages.map((video, index) => (
                      <div key={index}>
                        <h3>{video.modelName}</h3>
                        <video src={video.imageUrl} controls className='preview' />
                      </div>
                    ))
                  )
                ) : (
                  <div className='placeholder'>No annotated results available</div>
                )}
              </div>
            </div>
            <div className='csv-files'>
              <h3>CSV Files:</h3>
              {csvFileNames.length > 0 ? (
                <ul>
                  {csvFileNames.map((fileName, index) => (
                    <li key={index}>{fileName}</li>
                  ))}
                </ul>
              ) : (
                <div className='placeholder'>No CSV files available</div>
              )}
            </div>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
