import React, { useState } from 'react';
import WordCloudTimeline from '../components/WordCloudTimeline';
import './Dashboard.css';

/**
 * Dashboard Component
 *
 * Main intelligence visualization interface for the "Signal Radar" system.
 * Displays the WordCloudTimeline component which visualizes weak signals
 * and emerging keywords across time.
 *
 * Domain Context: This is the primary entry point for Corporate Affairs teams
 * to view real-time intelligence. The word cloud surfaces high-importance,
 * low-velocity keywords (weak signals) before they become mainstream news.
 */
function Dashboard() {
  const [settingsOpen, setSettingsOpen] = useState(false);

  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
  };

  return (
    <div className="dashboard-fullscreen">
      {/* Settings Button */}
      <button
        className={`settings-button ${settingsOpen ? 'active' : ''}`}
        onClick={toggleSettings}
        title="Filter Word Cloud Data"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </button>

      {/* Settings Panel */}
      <div className={`settings-panel ${settingsOpen ? 'open' : ''}`}>
        <div className="settings-header">
          <h3>Settings</h3>
          <button
            className="settings-close"
            onClick={toggleSettings}
            title="Close Settings"
          >
            ×
          </button>
        </div>

        <div className="settings-content">
          <div className="filter-group">
            <label className="filter-label">Current Sources</label>
            <div className="source-list">
              <div className="source-item">
                <input type="checkbox" id="source-newsapi" defaultChecked />
                <label htmlFor="source-newsapi">NewsAPI - Real-time news monitoring</label>
                <span className="source-metric">98% reliability</span>
              </div>
              <div className="source-item">
                <input type="checkbox" id="source-rss" defaultChecked />
                <label htmlFor="source-rss">RSS News Feeds - Major publications</label>
                <span className="source-metric">95% coverage</span>
              </div>
              <div className="source-item">
                <input type="checkbox" id="source-wikipedia" defaultChecked />
                <label htmlFor="source-wikipedia">Wikipedia - Company history & controversies</label>
                <span className="source-metric">92% accuracy</span>
              </div>
              <div className="source-item">
                <input type="checkbox" id="source-reddit" defaultChecked />
                <label htmlFor="source-reddit">Reddit - Community discussions</label>
                <span className="source-metric">87% engagement</span>
              </div>
              <div className="source-item">
                <input type="checkbox" id="source-sec" defaultChecked />
                <label htmlFor="source-sec">SEC EDGAR - US company filings</label>
                <span className="source-metric">100% compliance</span>
              </div>
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Add Custom Source</label>
            <div className="add-source-group">
              <select className="filter-select" id="new-source-type">
                <option value="">Select source type</option>
                <option value="news">News API</option>
                <option value="rss">RSS Feed</option>
                <option value="social">Social Media</option>
                <option value="regulatory">Regulatory</option>
                <option value="custom">Custom API</option>
              </select>
              <input
                type="text"
                placeholder="Source URL or API endpoint"
                className="filter-select"
                id="new-source-url"
              />
              <input
                type="text"
                placeholder="Source name (optional)"
                className="filter-select"
                id="new-source-name"
              />
              <button className="btn-primary-small">Add Source</button>
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Source Metrics Filter</label>
            <div className="metrics-filters">
              <label className="checkbox-label">
                <input type="checkbox" defaultChecked />
                High Reliability ({'>'}95%)
              </label>
              <label className="checkbox-label">
                <input type="checkbox" defaultChecked />
                Good Coverage ({'>'}90%)
              </label>
              <label className="checkbox-label">
                <input type="checkbox" defaultChecked />
                Recent Updates ({'<'}24h)
              </label>
              <label className="checkbox-label">
                <input type="checkbox" />
                Premium Sources Only
              </label>
            </div>
          </div>

          <div className="filter-actions">
            <button className="btn-secondary-small">Apply Settings</button>
            <button
              className="btn-outline-small"
              onClick={() => {
                // Reset to defaults
                const checkboxes = document.querySelectorAll('.source-item input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = true);
                const metricsCheckboxes = document.querySelectorAll('.metrics-filters input[type="checkbox"]');
                metricsCheckboxes.forEach(cb => cb.checked = true);
                document.getElementById('new-source-type').value = '';
                document.getElementById('new-source-url').value = '';
                document.getElementById('new-source-name').value = '';
              }}
            >
              Reset to Default
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <WordCloudTimeline />
      </div>
    </div>
  );
}

export default Dashboard;
