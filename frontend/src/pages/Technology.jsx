import React from 'react';

function Technology() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Technology Stack</h1>
          <p className="page-subtitle">
            Built on cutting-edge AI and proven enterprise technologies
          </p>
        </div>
      </section>

      <section className="section tech-section">
        <div className="section-content">
          <h2 className="section-title">Core Technologies</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <div className="tech-label">NLP Engine</div>
              <div className="tech-value">spaCy + scikit-learn</div>
            </div>
            <div className="tech-item">
              <div className="tech-label">Keyword Extraction</div>
              <div className="tech-value">TF-IDF, YAKE, Multi-word</div>
            </div>
            <div className="tech-item">
              <div className="tech-label">Sentiment Analysis</div>
              <div className="tech-value">VADER Algorithm</div>
            </div>
            <div className="tech-item">
              <div className="tech-label">Backend</div>
              <div className="tech-value">FastAPI + SQLAlchemy</div>
            </div>
            <div className="tech-item">
              <div className="tech-label">Frontend</div>
              <div className="tech-value">React + Vite</div>
            </div>
            <div className="tech-item">
              <div className="tech-label">Processing Speed</div>
              <div className="tech-value">&lt;500ms latency</div>
            </div>
          </div>

          <div className="tech-details">
            <div className="tech-section-card">
              <h3>🧠 Natural Language Processing</h3>
              <p>Our NLP pipeline is built on industry-leading open-source technologies:</p>
              <ul className="tech-list">
                <li><strong>spaCy</strong> - Industrial-strength NLP with pre-trained language models</li>
                <li><strong>scikit-learn</strong> - Machine learning algorithms for classification and clustering</li>
                <li><strong>TF-IDF</strong> - Statistical measure for keyword importance</li>
                <li><strong>YAKE</strong> - Unsupervised keyword extraction algorithm</li>
              </ul>
            </div>

            <div className="tech-section-card">
              <h3>⚡ Backend Architecture</h3>
              <p>High-performance, scalable backend infrastructure:</p>
              <ul className="tech-list">
                <li><strong>FastAPI</strong> - Modern, fast web framework with automatic API documentation</li>
                <li><strong>SQLAlchemy</strong> - Powerful ORM for database operations</li>
                <li><strong>Uvicorn</strong> - Lightning-fast ASGI server</li>
                <li><strong>Pydantic</strong> - Data validation using Python type annotations</li>
              </ul>
            </div>

            <div className="tech-section-card">
              <h3>🎨 Frontend Technologies</h3>
              <p>Modern, responsive user interface built with cutting-edge tools:</p>
              <ul className="tech-list">
                <li><strong>React 18</strong> - Component-based UI library with hooks</li>
                <li><strong>Vite</strong> - Next-generation frontend tooling with instant HMR</li>
                <li><strong>React Router</strong> - Declarative routing for React applications</li>
                <li><strong>Modern CSS</strong> - Flexbox, Grid, and CSS animations</li>
              </ul>
            </div>

            <div className="tech-section-card">
              <h3>🔒 Security & Infrastructure</h3>
              <p>Enterprise-grade security and reliability:</p>
              <ul className="tech-list">
                <li><strong>SQLite/PostgreSQL</strong> - Reliable data persistence</li>
                <li><strong>Content Hashing</strong> - Automatic deduplication</li>
                <li><strong>Rate Limiting</strong> - API protection and throttling</li>
                <li><strong>Input Validation</strong> - Comprehensive data validation</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="section features-section">
        <div className="section-content">
          <h2 className="section-title">Performance Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">&lt;500ms</div>
              <div className="metric-label">Processing Latency</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">1000+</div>
              <div className="metric-label">Documents/Second</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">99.9%</div>
              <div className="metric-label">Uptime SLA</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">50+</div>
              <div className="metric-label">Data Sources</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Technology;
