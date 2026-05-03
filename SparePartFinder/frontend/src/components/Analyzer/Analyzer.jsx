import React, { useState } from 'react';
import DropZone from './DropZone';
import Results from './Results';
import { predictPart } from '../../services/api';

const Analyzer = ({ onAddToHistory }) => {
  const [currentFile, setCurrentFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState(null);

  const handleFileSelect = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image.');
      return;
    }
    
    setCurrentFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleClear = () => {
    setCurrentFile(null);
    setImagePreview('');
    setResultData(null);
  };

  const handleAnalyze = async () => {
    if (!currentFile) return;

    setLoading(true);
    setResultData(null);

    try {
      const data = await predictPart(currentFile);
      setResultData(data);
      
      // Add to history with base64 image
      onAddToHistory({
        ...data,
        image_url: imagePreview
      });
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis error. Check console.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!resultData) return;
    
    let text = `SparePartFinder Pro Report\nPart: ${resultData.part_name} (${resultData.confidence})\n\n`;
    Object.entries(resultData.details).forEach(([k, v]) => text += `${k}: ${v}\n`);
    
    navigator.clipboard.writeText(text).then(() => {
      alert('Report copied to clipboard!');
    });
  };

  return (
    <section>
      <div className="analyzer-grid">
        <div className="upload-section">
          <div className="section-header">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '20px' }}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            Image Input
          </div>
          
          {!currentFile ? (
            <DropZone onFileSelect={handleFileSelect} />
          ) : (
            <div className="preview-box show">
              <img src={imagePreview} alt="Preview" />
            </div>
          )}
          
          <button
            className="btn btn-primary"
            disabled={!currentFile || loading}
            onClick={handleAnalyze}
            style={{ marginTop: '1.5rem' }}
          >
            {loading ? 'Processing...' : 'Start AI Processing'}
          </button>
          
          {currentFile && (
            <button className="btn btn-secondary" onClick={handleClear}>
              Reset Scanner
            </button>
          )}
        </div>

        <div className="results-pane">
          {loading && (
            <div className="loader">
              <div className="spinner"></div>
              <p style={{ fontWeight: '600', color: 'var(--primary)' }}>
                Running Deep Neural Network Analysis...
              </p>
            </div>
          )}

          {!loading && resultData && (
            <Results data={resultData} onCopy={handleCopy} />
          )}
        </div>
      </div>
    </section>
  );
};

export default Analyzer;
