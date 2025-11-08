import React from 'react';

function Features() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Platform Features</h1>
          <p className="page-subtitle">
            Discover the powerful capabilities that make Perceptron the ultimate intelligence platform
          </p>
        </div>
      </section>

      <section className="section features-section">
        <div className="section-content">
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Multi-Source Aggregation</h3>
              <p>Connect to unlimited data sources including RSS feeds, REST APIs, webhooks, and custom integrations. Our platform automatically normalizes and structures incoming data for seamless processing.</p>
              <ul className="feature-list">
                <li>RSS and Atom feed support</li>
                <li>RESTful API integrations</li>
                <li>Webhook receivers</li>
                <li>Custom data connectors</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-Time Processing</h3>
              <p>Process thousands of documents per second with our highly optimized pipeline. Sub-500ms latency ensures you get insights the moment they matter.</p>
              <ul className="feature-list">
                <li>Parallel processing architecture</li>
                <li>In-memory caching</li>
                <li>Intelligent load balancing</li>
                <li>Auto-scaling capabilities</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Smart Keyword Extraction</h3>
              <p>Advanced NLP algorithms powered by TF-IDF, spaCy, and YAKE extract the most relevant keywords and phrases from your content automatically.</p>
              <ul className="feature-list">
                <li>Multi-word phrase detection</li>
                <li>Contextual relevance scoring</li>
                <li>Domain-specific tuning</li>
                <li>Stop-word filtering</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Sentiment Analysis</h3>
              <p>Understand the emotional tone and sentiment behind every piece of content using state-of-the-art VADER sentiment analysis.</p>
              <ul className="feature-list">
                <li>Positive/negative/neutral detection</li>
                <li>Intensity scoring</li>
                <li>Entity-level sentiment</li>
                <li>Trend analysis over time</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Beautiful Visualizations</h3>
              <p>Transform complex data into stunning, interactive visualizations that make insights immediately actionable.</p>
              <ul className="feature-list">
                <li>Dynamic word clouds</li>
                <li>Time-series analytics</li>
                <li>Team-specific dashboards</li>
                <li>Custom reporting</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h3>Enterprise Security</h3>
              <p>Bank-grade security features ensure your sensitive intelligence data remains protected at all times.</p>
              <ul className="feature-list">
                <li>Role-based access control (RBAC)</li>
                <li>End-to-end encryption</li>
                <li>Audit logging</li>
                <li>SOC 2 compliance</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="section cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to experience these features?</h2>
          <p className="cta-subtitle">Start your free trial today</p>
          <button className="btn-primary btn-large">Get Started</button>
        </div>
      </section>
    </div>
  );
}

export default Features;
