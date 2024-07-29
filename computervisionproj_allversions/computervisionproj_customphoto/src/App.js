import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [selectedType, setSelectedType] = useState(null); // 'image' or 'video'
  const [originalFileUrl, setOriginalFileUrl] = useState(null);
  const [annotatedFileUrl, setAnnotatedFileUrl] = useState(null);
  const [annotations, setAnnotations] = useState([]);
  const [boundingBoxes, setBoundingBoxes] = useState([]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    console.debug('File selected: ' + selectedFile.name);
    setFile(selectedFile);
    setOriginalFileUrl(URL.createObjectURL(selectedFile));
    setAnnotatedFileUrl(null);
    setAnnotations([]);
    setBoundingBoxes([]);
  };

  const handleUpload = async () => {
    if (!file || !selectedType) return;

    console.debug('Uploading ' + selectedType + ': ' + file.name);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.debug('Upload Response: ' + JSON.stringify(uploadResponse.data));

      const { csv_file_name } = uploadResponse.data;

      // Fetch annotations after upload
      const annotationsResponse = await axios.get('http://localhost:5000/fetch-annotations', {
        params: { csv_file_name }
      });
      console.debug('Annotations Response: ' + JSON.stringify(annotationsResponse.data));
      setAnnotations(annotationsResponse.data.labels);

    } catch (error) {
      console.error('Error uploading ' + selectedType + ':', error);
    }
  };

  const handleClear = () => {
    console.debug('Clearing all fields');
    setFile(null);
    setSelectedType(null);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setAnnotations([]);
    setBoundingBoxes([]);
  };

  const handleAnnotationClick = async (annotation) => {
    console.log('Annotation clicked:', annotation);
    try {
      const searchResponse = await axios.post('http://localhost:5000/search', {
        filename: `detections_${file.name.split('.')[0]}`, // Match CSV filename format
        query: annotation
      });
      console.debug('Search Response: ' + JSON.stringify(searchResponse.data));

      // Convert bounding box strings to arrays of numbers
      const parsedBoxes = searchResponse.data.boxes.map(boxString => JSON.parse(boxString));
      setBoundingBoxes(parsedBoxes);

      // Clear previously set annotated image URL before setting a new one
      setAnnotatedFileUrl(null);

      // Generate annotated image
      const generateImageResponse = await axios.post('http://localhost:5000/generate-image', {
        image_path: `static/uploads/${file.name}`, // Path to the original image
        boxes: parsedBoxes
      });
      console.debug('Generate Image Response: ' + JSON.stringify(generateImageResponse.data));

      // Set URL for annotated image
      const uniqueId = new Date().getTime(); // Generate a unique ID based on the current timestamp
      setAnnotatedFileUrl(`http://localhost:5000/${generateImageResponse.data.annotated_image_path}?${uniqueId}`);

    } catch (error) {
      console.error('Error searching annotation:', error);
      if (error.response) {
        console.error('Response error:', error.response.data);
      }
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
                    <video controls className='preview'>
                      <source src={originalFileUrl} type={file.type} />
                      Your browser does not support the video tag.
                    </video>
                  )
                ) : (
                  <div className='placeholder'>No {selectedType} selected</div>
                )}
              </div>
              <div className='media-box'>
                <h2>Annotated {selectedType === 'image' ? 'Image' : 'Video'}</h2>
                {annotatedFileUrl ? (
                  <img src={annotatedFileUrl} alt='Annotated' className='preview' />
                ) : (
                  <div className='placeholder'>No annotated {selectedType} available</div>
                )}
              </div>
            </div>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
