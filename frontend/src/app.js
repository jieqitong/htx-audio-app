import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [files, setFiles] = useState([]);
  const [transcriptions, setTranscriptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearched, setIsSearched] = useState(false);

  useEffect(() => {
    fetchTranscriptions();
  }, []);

  const fetchTranscriptions = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/transcriptions`);
      if (response) {
        setTranscriptions(response.data);
      }
      setSearchTerm('');
      setIsSearched(false);
    } catch (error) {
      console.error('Error fetching transcriptions:', error);
    }
  };

  const handleFileChange = (event) => {
    setFiles(event.target.files);
  };

  const handleUpload = async () => {
    setIsLoading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/transcribe`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      fetchTranscriptions();
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsLoading(false); // stop loading
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/search?audio_filename=${searchTerm}`);
      setTranscriptions(response.data);
      setIsSearched(true);
    } catch (error) {
      console.error('Error searching transcriptions:', error);
    }
  };

  return (
    <div>
      <h1>Audio Transcription App</h1>
      
      <h2>Upload Audio File(s)</h2>
      <input type="file" multiple onChange={handleFileChange} data-testid="file-upload-input"/>
      <button onClick={handleUpload} disabled={isLoading || (files.length == 0)}>Upload</button>


      <h2>Search by Audio Filename</h2>
      <div>
        <input
          type="text"
          placeholder="Search by filename"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
        <button onClick={fetchTranscriptions}>Reset Search</button>
      </div>

      {isLoading && (
        <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', backgroundColor: 'white', padding: '20px', border: '1px solid #ccc' }}>
          Loading...
        </div>
      )}

      <h2>Transcriptions</h2>
      {transcriptions.length ? (
        <table id="transcriptions_table">
        <thead><tr>
          <th>Audio Filename</th>
          <th>Transribed Text</th>
          <th>Created Timestamp</th>
        </tr></thead>
        <tbody>
        {transcriptions.map((transcription) => (
          <tr key={transcription.created_at}>
            <td>{transcription.audio_filename}</td>
            <td>{transcription.transcribed_text}</td>
            <td>{transcription.created_at}</td>
          </tr>
        ))}
        </tbody>
      </table>
      ) : (isSearched ? <div>No Matched Filename</div> : <div>No Transcription Stored</div>)}
    </div>
  );
}

export default App;