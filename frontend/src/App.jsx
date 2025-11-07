import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiMessage, setApiMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/hello')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch from API');
        }
        return response.json();
      })
      .then(data => {
        setApiMessage(data.message);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Signal Radar</h1>
        <p className="subtitle">Deutsche Bank Intelligence Dashboard</p>
      </header>

      <main className="app-main">
        <div className="card">
          <h2>Frontend Status</h2>
          <p className="status-ok">✅ React + Vite running</p>
        </div>

        <div className="card">
          <h2>Backend Connection</h2>
          {loading && <p className="status-loading">⏳ Connecting...</p>}
          {error && (
            <div>
              <p className="status-error">❌ Connection failed</p>
              <p className="error-details">{error}</p>
              <p className="hint">
                Make sure the backend is running on port 8000
              </p>
            </div>
          )}
          {!loading && !error && (
            <div>
              <p className="status-ok">✅ Connected to API</p>
              <p className="api-response">{apiMessage}</p>
            </div>
          )}
        </div>

        <div className="card">
          <h3>Quick Commands</h3>
          <ul className="command-list">
            <li>
              <code>cd frontend && npm run dev</code> - Start frontend
            </li>
            <li>
              <code>cd backend && ./run.sh</code> - Start backend
            </li>
            <li>
              <code>npm run format</code> - Format code
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default App;
