import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [selectedType, setSelectedType] = useState(null); // 'image' or 'video'
  const [originalFileUrl, setOriginalFileUrl] = useState(null);
  const [annotatedFileUrl, setAnnotatedFileUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!file || !selectedType) return;

    // Show the original image or video immediately
    setOriginalFileUrl(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', selectedType);

    try {
      const response = await axios.post('/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        }
      });

      const { annotated_file } = response.data;
      setAnnotatedFileUrl(annotated_file);
      setUploadProgress(0);
    } catch (error) {
      console.error(`Error uploading ${selectedType}:`, error);
      setUploadProgress(0);
    }
  };

  const handleClear = () => {
    setFile(null);
    setSelectedType(null);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
  };

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    setFile(null);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Image and Video Processing App</h1>
        <div>
          <button onClick={() => handleTypeSelect('image')} disabled={selectedType === 'image'}>Process Image</button>
          <button onClick={() => handleTypeSelect('video')} disabled={selectedType === 'video'}>Process Video</button>
        </div>
        {selectedType && (
          <>
            <label>
              Choose File:
              <input type="file" accept={selectedType === 'image' ? 'image/*' : 'video/*'} onChange={handleFileChange} />
            </label>
            <button onClick={handleUpload} disabled={!file}>Upload and Process</button>
            <button onClick={handleClear}>Clear</button>
            {uploadProgress > 0 && <p>Upload Progress: {uploadProgress}%</p>}
            <div className="media-container">
              <div className="media-box">
                <h2>Original {selectedType === 'image' ? 'Image' : 'Video'}</h2>
                {originalFileUrl ? (
                  selectedType === 'image' ? (
                    <img src={originalFileUrl} alt="Original" className="preview" />
                  ) : (
                    <video controls className="preview">
                      <source src={originalFileUrl} type={file.type} />
                      Your browser does not support the video tag.
                    </video>
                  )
                ) : (
                  <div className="placeholder">No {selectedType} selected</div>
                )}
              </div>
              <div className="media-box">
                <h2>Annotated {selectedType === 'image' ? 'Image' : 'Video'}</h2>
                {annotatedFileUrl ? (
                  selectedType === 'image' ? (
                    <img src={annotatedFileUrl} alt="Annotated" className="preview" />
                  ) : (
                    <video controls className="preview">
                      <source src={annotatedFileUrl} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  )
                ) : (
                  <div className="placeholder">No {selectedType} annotated</div>
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