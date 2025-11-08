import React from 'react';

function Features() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Powerful Features for Modern Intelligence</h1>
          <p className="page-subtitle">
            From data aggregation to actionable insights—Perceptron transforms how teams monitor, analyze, and act on critical information in real-time
          </p>
        </div>
      </section>

      {/* Core Platform Features */}
      <section className="section features-section">
        <div className="section-content">
          <div className="section-header">
            <h2 className="section-title">Core Platform Capabilities</h2>
            <p className="section-description">Enterprise-grade tools built for scale, speed, and intelligence</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Multi-Source Data Aggregation</h3>
              <p>Perceptron connects seamlessly to diverse information sources, creating a unified intelligence hub. Our extensible sourcer architecture supports RSS feeds, REST APIs, webhooks, and custom integrations—all processed through a single pipeline.</p>
              <ul className="feature-list">
                <li><strong>RSS & Atom Feeds:</strong> Monitor news, blogs, podcasts, and industry publications</li>
                <li><strong>REST APIs:</strong> Pull data from third-party services and internal systems</li>
                <li><strong>Webhook Receivers:</strong> Real-time push notifications from external platforms</li>
                <li><strong>Custom Sourcers:</strong> Build your own connectors with our Python SDK</li>
                <li><strong>Scheduled Polling:</strong> Configurable refresh intervals (1min - 24hrs)</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>Advanced NLP & Keyword Extraction</h3>
              <p>Extract meaningful insights from unstructured text using cutting-edge natural language processing. Our multi-algorithm approach combines TF-IDF, YAKE, spaCy NER, and custom importance scoring to identify the keywords that truly matter.</p>
              <ul className="feature-list">
                <li><strong>Multi-Algorithm Extraction:</strong> TF-IDF, YAKE, TextRank, and hybrid models</li>
                <li><strong>Entity Recognition:</strong> Automatically detect people, organizations, locations, and products</li>
                <li><strong>Phrase Detection:</strong> Capture multi-word expressions and domain terminology</li>
                <li><strong>Importance Scoring:</strong> Rank keywords by relevance, frequency, and context</li>
                <li><strong>Language Support:</strong> Process content in 100+ languages</li>
                <li><strong>Custom Filters:</strong> Define stop words and exclusion rules per team</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Team-Based Intelligence</h3>
              <p>Organize intelligence gathering around your organizational structure. Each team gets customized data sources, keyword tracking, and dashboards tailored to their specific monitoring needs.</p>
              <ul className="feature-list">
                <li><strong>Unlimited Teams:</strong> Create teams for different departments, projects, or focus areas</li>
                <li><strong>Team Personas:</strong> Competitor, Investor, Regulator, Researcher perspectives</li>
                <li><strong>Custom Sources:</strong> Each team monitors its own set of feeds and APIs</li>
                <li><strong>Isolated Analytics:</strong> Team-specific keyword trends and insights</li>
                <li><strong>Collaboration Tools:</strong> Share insights and reports across teams</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-Time Processing Pipeline</h3>
              <p>Process thousands of articles per second with sub-second latency. Our async architecture powered by FastAPI and Python ensures you never miss critical intelligence, even during high-volume periods.</p>
              <ul className="feature-list">
                <li><strong>Asynchronous Processing:</strong> Non-blocking I/O for maximum throughput</li>
                <li><strong>Intelligent Deduplication:</strong> Automatically detect and filter duplicate content</li>
                <li><strong>Incremental Updates:</strong> Only fetch new content since last check</li>
                <li><strong>Background Scheduling:</strong> APScheduler manages automated data collection</li>
                <li><strong>Error Recovery:</strong> Automatic retry logic with exponential backoff</li>
                <li><strong>Performance Monitoring:</strong> Real-time metrics on processing speed and health</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Interactive Visualizations</h3>
              <p>Transform raw data into actionable insights with beautiful, interactive charts. Our visualization suite uses Recharts and D3.js to create word clouds, time-series graphs, sentiment trends, and comparative analytics.</p>
              <ul className="feature-list">
                <li><strong>Dynamic Word Clouds:</strong> Visualize keyword frequency and importance</li>
                <li><strong>Time-Series Analysis:</strong> Track keyword mentions over time</li>
                <li><strong>Team Comparisons:</strong> Compare keyword usage across different teams</li>
                <li><strong>Sentiment Heatmaps:</strong> See emotional tone patterns at a glance</li>
                <li><strong>Export Options:</strong> Download charts as PNG, SVG, or CSV</li>
                <li><strong>Responsive Design:</strong> Optimized for desktop, tablet, and mobile</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Sentiment & Emotion Analysis</h3>
              <p>Understand not just what is being said, but how it&apos;s being said. Our sentiment engine analyzes tone, emotion, and intensity to help you gauge public perception and detect emerging narratives.</p>
              <ul className="feature-list">
                <li><strong>VADER Sentiment:</strong> Social media-optimized sentiment scoring</li>
                <li><strong>Compound Scores:</strong> Overall sentiment from -1 (negative) to +1 (positive)</li>
                <li><strong>Emotion Detection:</strong> Identify joy, anger, sadness, fear, and surprise</li>
                <li><strong>Entity-Level Sentiment:</strong> Track sentiment toward specific entities</li>
                <li><strong>Trend Analysis:</strong> Monitor sentiment shifts over time</li>
                <li><strong>Alert Triggers:</strong> Get notified when sentiment crosses thresholds</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Data Storage & Architecture */}
      <section className="section features-section alternate">
        <div className="section-content">
          <div className="section-header">
            <h2 className="section-title">Enterprise Architecture</h2>
            <p className="section-description">Built on proven technologies for reliability and scale</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">💾</div>
              <h3>Dual-Database Architecture</h3>
              <p>Perceptron uses a sophisticated dual-database design optimized for different data access patterns.</p>
              <ul className="feature-list">
                <li><strong>MongoDB (Azure Cosmos DB):</strong> User authentication, team config, and metadata</li>
                <li><strong>SQLite Data Lake:</strong> High-performance storage for articles, keywords, and analytics</li>
                <li><strong>Automatic Indexing:</strong> Optimized queries for millisecond response times</li>
                <li><strong>Incremental Backups:</strong> Point-in-time recovery for peace of mind</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h3>Security & Authentication</h3>
              <p>Enterprise-grade security features protect your intelligence data at every layer.</p>
              <ul className="feature-list">
                <li><strong>JWT Authentication:</strong> Secure, stateless token-based auth</li>
                <li><strong>BCrypt Password Hashing:</strong> Industry-standard credential protection</li>
                <li><strong>Azure Cosmos DB:</strong> Multi-region replication and 99.999% SLA</li>
                <li><strong>HTTPS/TLS:</strong> End-to-end encryption for all data in transit</li>
                <li><strong>CORS Protection:</strong> Configurable origin policies</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🚀</div>
              <h3>Modern Tech Stack</h3>
              <p>Built with cutting-edge technologies for performance, maintainability, and developer experience.</p>
              <ul className="feature-list">
                <li><strong>Backend:</strong> Python 3.12, FastAPI, Uvicorn, PyMongo</li>
                <li><strong>Frontend:</strong> React 18, Vite, React Router, Recharts</li>
                <li><strong>NLP:</strong> spaCy, YAKE, NLTK, scikit-learn</li>
                <li><strong>Database:</strong> Azure Cosmos DB (MongoDB API), SQLite</li>
                <li><strong>Scheduling:</strong> APScheduler for automated tasks</li>
              </ul>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚙️</div>
              <h3>Easy Configuration & Deployment</h3>
              <p>Get up and running in minutes with simple configuration and flexible deployment options.</p>
              <ul className="feature-list">
                <li><strong>JSON Configuration:</strong> Human-readable team and source setup</li>
                <li><strong>Environment Variables:</strong> Secure credential management</li>
                <li><strong>Docker Support:</strong> Containerized deployment ready</li>
                <li><strong>CLI Tools:</strong> Setup scripts for database initialization</li>
                <li><strong>Hot Reload:</strong> Changes apply without service restart</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="section features-section">
        <div className="section-content">
          <div className="section-header">
            <h2 className="section-title">Real-World Use Cases</h2>
            <p className="section-description">See how teams use Perceptron to stay ahead</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🏢</div>
              <h3>Competitive Intelligence</h3>
              <p>Monitor competitor announcements, product launches, funding rounds, and market positioning in real-time. Track mentions across news, blogs, and social media.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">💰</div>
              <h3>Investment Research</h3>
              <p>Track market trends, emerging technologies, funding activity, and industry shifts. Build custom dashboards for portfolio companies and investment themes.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚖️</div>
              <h3>Regulatory Monitoring</h3>
              <p>Stay compliant with automated monitoring of regulatory updates, policy changes, and compliance requirements across multiple jurisdictions.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔬</div>
              <h3>Research & Development</h3>
              <p>Track scientific publications, patent filings, conference proceedings, and breakthrough research in your field. Never miss a critical development.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📰</div>
              <h3>Media Monitoring</h3>
              <p>Track brand mentions, industry news, and public perception across thousands of media sources. Measure share of voice and sentiment trends.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎓</div>
              <h3>Academic Research</h3>
              <p>Aggregate research papers, preprints, and academic discussions. Track citations, author collaborations, and emerging research directions.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Features;
