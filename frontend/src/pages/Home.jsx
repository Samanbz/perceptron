import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="hero-title-line">Intelligence that</span>
            <span className="hero-title-line gradient-text">
              sees everything.
            </span>
          </h1>
          <p className="hero-subtitle">
            Transform information overload into actionable intelligence.
            <br />
            Powered by advanced NLP and real-time signal processing.
          </p>
          <div className="hero-cta">
            <Link to="/dashboard" className="btn-primary">
              Explore Platform
            </Link>
            <button className="btn-secondary">Watch Demo</button>
          </div>
          <div className="hero-visual">
            <div className="visual-grid">
              <div className="visual-card card-1">
                <div className="card-icon">📊</div>
                <div className="card-label">Real-time Analytics</div>
              </div>
              <div className="visual-card card-2">
                <div className="card-icon">🧠</div>
                <div className="card-label">NLP Processing</div>
              </div>
              <div className="visual-card card-3">
                <div className="card-icon">🎯</div>
                <div className="card-label">Signal Detection</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="section features-section">
        <div className="section-content">
          <h2 className="section-title">Built for modern intelligence.</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Multi-Source Aggregation</h3>
              <p>
                Seamlessly integrate data from RSS feeds, APIs, and custom
                sources. One platform, infinite insights.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-Time Processing</h3>
              <p>
                Process thousands of signals per second with sub-second latency.
                Intelligence at the speed of thought.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Smart Keyword Extraction</h3>
              <p>
                Advanced NLP algorithms identify critical keywords using TF-IDF,
                spaCy, and YAKE methodologies.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Sentiment Analysis</h3>
              <p>
                Understand the emotional context behind every signal with VADER
                sentiment scoring.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Beautiful Visualizations</h3>
              <p>
                Interactive word clouds, time-series charts, and team dashboards
                that make data beautiful.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h3>Enterprise Security</h3>
              <p>
                Bank-grade security with role-based access control and encrypted
                data storage.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Intelligence Teams Section */}
      <section id="teams" className="section teams-section">
        <div className="section-content">
          <h2 className="section-title">Four teams. One mission.</h2>
          <p className="section-subtitle">
            Specialized intelligence units working in perfect harmony
          </p>
          <div className="teams-grid">
            <div className="team-card team-regulator">
              <div className="team-icon">⚖️</div>
              <h3>Regulatory Team</h3>
              <p>
                Monitor compliance requirements, government policies, and
                regulatory changes across federal agencies.
              </p>
              <div className="team-badge">Real-time alerts</div>
            </div>
            <div className="team-card team-investor">
              <div className="team-icon">📊</div>
              <h3>Investment Team</h3>
              <p>
                Track market trends, funding rounds, M&A activity, and emerging
                investment opportunities.
              </p>
              <div className="team-badge">Market intelligence</div>
            </div>
            <div className="team-card team-competitor">
              <div className="team-icon">👁️</div>
              <h3>Competitive Intelligence</h3>
              <p>
                Monitor competitor activities, product launches, and strategic
                positioning in real-time.
              </p>
              <div className="team-badge">Strategic insights</div>
            </div>
            <div className="team-card team-researcher">
              <div className="team-icon">🔬</div>
              <h3>Research Team</h3>
              <p>
                Track emerging technologies, academic research, and technical
                innovations across disciplines.
              </p>
              <div className="team-badge">Innovation radar</div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section id="technology" className="section tech-section">
        <div className="section-content">
          <h2 className="section-title">Powered by cutting-edge AI.</h2>
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
        </div>
      </section>

      {/* CTA Section */}
      <section className="section cta-section">
        <div className="cta-content">
          <h2 className="cta-title">
            Ready to transform your intelligence workflow?
          </h2>
          <p className="cta-subtitle">
            Join organizations using Perceptron to stay ahead.
          </p>
          <button className="btn-primary btn-large">Get Started Today</button>
        </div>
      </section>
    </>
  );
}

export default Home;
