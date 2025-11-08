import React from 'react';
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
  return (
    <div className="dashboard-fullscreen">
      <WordCloudTimeline />
    </div>
  );
}

export default Dashboard;
