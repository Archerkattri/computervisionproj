import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [originalImage, setOriginalImage] = useState(null);
  const [annotatedImage, setAnnotatedImage] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setOriginalImage(null);
    setAnnotatedImage(null);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

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

      const { annotated_image } = response.data;
      setAnnotatedImage(annotated_image);
      setUploadProgress(0);
      setOriginalImage(URL.createObjectURL(file));
    } catch (error) {
      console.error('Error uploading image:', error);
      setUploadProgress(0);
    }
  };

  const handleClear = () => {
    setFile(null);
    setOriginalImage(null);
    setAnnotatedImage(null);
    setUploadProgress(0);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Processing App</h1>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={!file}>Upload and Process</button>
        <button onClick={handleClear}>Clear</button>
        {uploadProgress > 0 && <p>Upload Progress: {uploadProgress}%</p>}
        {originalImage && <img src={originalImage} alt="Original" className="preview" />}
        {annotatedImage && <img src={annotatedImage} alt="Annotated" className="preview" />}
      </header>
    </div>
  );
}

export default App;