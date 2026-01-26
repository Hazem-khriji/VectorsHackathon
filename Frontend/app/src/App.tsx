import ReactMarkdown from 'react-markdown';
import { useState, useRef } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('query', query);
      if (image) {
        formData.append('image', image);
      }

      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      if (data.success) {
        setResult(data.data || JSON.stringify(data, null, 2));
      } else {
        throw new Error(data.error || 'An error occurred');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuery('');
    setImage(null);
    setImagePreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="container">
      <div className="header">
        <div className="header-icon">🔍</div>
        <h1>Product Search</h1>
        <p className="subtitle">Search products using text or images</p>
      </div>

      <div className="form-group">
        <label htmlFor="query">Search Query</label>
        <input
          type="text"
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you're looking for..."
        />
      </div>

      <div className="form-group">
        <label>Image (Optional)</label>
        <div className="file-upload-wrapper">
          <label 
            htmlFor="image" 
            className={`file-upload-label ${imagePreview ? 'has-file' : ''}`}
          >
            <span className="upload-icon">📷</span>
            <span className="upload-text">
              <strong>Click to upload</strong> or drag and drop<br />
              PNG, JPG, WEBP up to 10MB
            </span>
          </label>
          <input
            type="file"
            id="image"
            ref={fileInputRef}
            accept="image/*"
            onChange={handleImageChange}
          />
        </div>
        {imagePreview && (
          <div id="imagePreview">
            <img src={imagePreview} alt="Preview" />
            {image && <p className="image-name">{image.name}</p>}
          </div>
        )}
      </div>

      <div className="button-group">
        <button onClick={handleSearch} disabled={loading} className="search-btn">
          {loading ? <span className="spinner"></span> : <>🔍 Search</>}
        </button>
        <button onClick={handleReset} className="reset-btn" disabled={loading}>
          ↺ Reset
        </button>
      </div>

      {error && (
        <div className="error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {result && (
        <div className="results">
          <div className="results-header">
            <span className="results-icon">✨</span>
            <h2>Results</h2>
          </div>
          <div id="resultsContent">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
