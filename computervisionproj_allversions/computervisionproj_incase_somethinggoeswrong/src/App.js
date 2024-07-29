import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [selectedType, setSelectedType] = useState(null); // 'image' or 'video'
  const [originalFileUrl, setOriginalFileUrl] = useState(null);
  const [annotatedFileUrl, setAnnotatedFileUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [readyToSearch, setReadyToSearch] = useState(false); // To indicate readiness for search

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    console.debug(`File selected: ${selectedFile.name}`);
    setFile(selectedFile);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
    setReadyToSearch(false); // Reset search readiness
  };

  const handleUpload = async () => {
    if (!file || !selectedType) return;

    setOriginalFileUrl(URL.createObjectURL(file));
    console.debug(`Uploading ${selectedType}: ${file.name}`);

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
          console.debug(`Upload progress: ${progress}%`);
        }
      });

      setReadyToSearch(response.data.ready_to_search); // Update readiness for search
      console.debug(`Response from server: ${JSON.stringify(response.data)}`);
      setUploadProgress(0);

      // Fetch all categories for suggestions after file processing
      const categoryResponse = await axios.get('/coco_categories');
      const allLabels = Object.values(categoryResponse.data);
      setSuggestions(allLabels); // Set all categories as suggestions
      console.debug(`Fetched categories for suggestions: ${allLabels}`);
    } catch (error) {
      console.error(`Error uploading ${selectedType}:`, error);
      setUploadProgress(0);
    }
  };

  const handleClear = async () => {
    console.debug('Clearing all fields');
    await axios.post('/clear'); // Clear files on the server
    setFile(null);
    setSelectedType(null);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
    setSearchQuery('');
    setSuggestions([]);
    setReadyToSearch(false); // Reset search readiness
  };

  const handleTypeSelect = (type) => {
    console.debug(`File type selected: ${type}`);
    setSelectedType(type);
    setFile(null);
    setOriginalFileUrl(null);
    setAnnotatedFileUrl(null);
    setUploadProgress(0);
    setReadyToSearch(false); // Reset search readiness
  };

  const handleSearch = async () => {
    if (!searchQuery || !readyToSearch) return;

    const csvFilename = file.name.replace(/ /g, '_') + '.csv'; // Replace spaces with underscores
    console.debug(`Searching for annotation: "${searchQuery}" in file: ${csvFilename}`);

    try {
      const response = await axios.post('/search', {
        filename: csvFilename,
        query: searchQuery.trim()
      });

      if (response.data.annotated_image_path) {
        setAnnotatedFileUrl(response.data.annotated_image_path);
        console.debug(`Annotated file available at: ${response.data.annotated_image_path}`);
      } else {
        alert(`The annotation "${searchQuery}" is not available in this file.`);
      }
    } catch (error) {
      console.error('Error searching for annotation:', error);
    }
  };

  const handleSearchChange = (event) => {
    const query = event.target.value;
    console.debug(`Search query changed: "${query}"`);
    setSearchQuery(query);

    // Filter suggestions based on current query
    if (suggestions.length > 0) {
      const filteredSuggestions = suggestions.filter((suggestion) =>
        suggestion.toLowerCase().startsWith(query.toLowerCase())
      );
      setSuggestions(filteredSuggestions);
      console.debug(`Filtered suggestions: ${filteredSuggestions}`);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    console.debug(`Suggestion clicked: "${suggestion}"`);
    setSearchQuery(suggestion);
    setSuggestions([]); // Clear suggestions after selection
  };

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/coco_categories');
        setSuggestions(Object.values(response.data)); // Set categories as suggestions
        console.debug(`Categories fetched on mount: ${Object.values(response.data)}`);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

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
            {readyToSearch && <p>You can start searching now!</p>}
            <div className="search-container">
              <input
                type="text"
                className="search-bar"
                placeholder="Search for annotations..."
                value={searchQuery}
                onChange={handleSearchChange}
              />
              <button onClick={handleSearch} disabled={!readyToSearch}>Search</button>
              {suggestions.length > 0 && (
                <ul className="suggestions" style={{ marginTop: '5px' }}>
                  {suggestions.map((suggestion, index) => (
                    <li key={index} className="suggestion-item" onClick={() => handleSuggestionClick(suggestion)}>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              )}
            </div>
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
