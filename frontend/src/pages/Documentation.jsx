import React from 'react';

function Documentation() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Documentation</h1>
          <p className="page-subtitle">
            Complete guides, API references, and tutorials to get you started
          </p>
        </div>
      </section>

      <section className="section features-section">
        <div className="section-content">
          <div className="docs-grid">
            <div className="docs-card">
              <div className="docs-icon">📚</div>
              <h3>Getting Started</h3>
              <p>Quick start guide to set up Perceptron in minutes.</p>
              <a href="#" className="docs-link">Read Guide →</a>
            </div>

            <div className="docs-card">
              <div className="docs-icon">🔧</div>
              <h3>Configuration</h3>
              <p>Configure teams, sources, and keyword extraction settings.</p>
              <a href="#" className="docs-link">View Config →</a>
            </div>

            <div className="docs-card">
              <div className="docs-icon">🔌</div>
              <h3>API Reference</h3>
              <p>Complete REST API documentation with examples.</p>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="docs-link">
                Open API Docs →
              </a>
            </div>

            <div className="docs-card">
              <div className="docs-icon">📊</div>
              <h3>Data Models</h3>
              <p>Understand the data structures and schemas.</p>
              <a href="#" className="docs-link">Explore Models →</a>
            </div>

            <div className="docs-card">
              <div className="docs-icon">🎯</div>
              <h3>Best Practices</h3>
              <p>Tips and recommendations for optimal performance.</p>
              <a href="#" className="docs-link">Learn More →</a>
            </div>

            <div className="docs-card">
              <div className="docs-icon">💡</div>
              <h3>Tutorials</h3>
              <p>Step-by-step tutorials for common use cases.</p>
              <a href="#" className="docs-link">Start Learning →</a>
            </div>
          </div>

          <div className="code-example-section">
            <h2 className="section-title">Quick Example</h2>
            <div className="code-example">
              <h4>Fetch Latest Intelligence Signals</h4>
              <pre><code>{`# Python Example
import requests

# Get latest signals from all teams
response = requests.get('http://localhost:8000/api/signals')
signals = response.json()

for signal in signals:
    print(f"Team: {signal['team']}")
    print(f"Keywords: {', '.join(signal['keywords'])}")
    print(f"Sentiment: {signal['sentiment']}")
    print("---")
`}</code></pre>
            </div>

            <div className="code-example">
              <h4>Subscribe to Team Updates</h4>
              <pre><code>{`# JavaScript Example
const teamUpdates = await fetch(
  'http://localhost:8000/api/teams/regulator/signals'
);
const data = await teamUpdates.json();

data.signals.forEach(signal => {
  console.log(\`New signal: \${signal.title}\`);
  console.log(\`Keywords: \${signal.keywords.join(', ')}\`);
});
`}</code></pre>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Documentation;
