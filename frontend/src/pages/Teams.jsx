import React from 'react';

function Teams() {
  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Intelligence Teams</h1>
          <p className="page-subtitle">
            Four specialized teams working together to provide comprehensive market intelligence
          </p>
        </div>
      </section>

      <section className="section teams-section">
        <div className="section-content">
          <div className="teams-detail-grid">
            <div className="team-detail-card team-regulator">
              <div className="team-header">
                <div className="team-icon-large">⚖️</div>
                <div>
                  <h2>Regulatory Team</h2>
                  <div className="team-badge">Real-time alerts</div>
                </div>
              </div>
              <p className="team-description">
                The Regulatory Team monitors compliance requirements, government policies, and regulatory changes across federal agencies. Stay ahead of regulatory shifts that could impact your business.
              </p>
              <div className="team-features">
                <h4>Key Capabilities:</h4>
                <ul>
                  <li>Federal Register monitoring</li>
                  <li>SEC newsroom tracking</li>
                  <li>Regulatory change alerts</li>
                  <li>Compliance deadline tracking</li>
                  <li>Policy impact analysis</li>
                </ul>
              </div>
              <div className="team-sources">
                <h4>Data Sources:</h4>
                <p>Federal Register, SEC Newsroom, Reuters Regulatory, Government Agencies</p>
              </div>
            </div>

            <div className="team-detail-card team-investor">
              <div className="team-header">
                <div className="team-icon-large">📊</div>
                <div>
                  <h2>Investment Team</h2>
                  <div className="team-badge">Market intelligence</div>
                </div>
              </div>
              <p className="team-description">
                Track market trends, funding rounds, M&A activity, and emerging investment opportunities in real-time. Make data-driven investment decisions with comprehensive market intelligence.
              </p>
              <div className="team-features">
                <h4>Key Capabilities:</h4>
                <ul>
                  <li>Funding round tracking</li>
                  <li>M&A activity monitoring</li>
                  <li>Market trend analysis</li>
                  <li>Startup ecosystem insights</li>
                  <li>Investment opportunity alerts</li>
                </ul>
              </div>
              <div className="team-sources">
                <h4>Data Sources:</h4>
                <p>TechCrunch, VentureBeat, Crunchbase News, Financial Markets</p>
              </div>
            </div>

            <div className="team-detail-card team-competitor">
              <div className="team-header">
                <div className="team-icon-large">👁️</div>
                <div>
                  <h2>Competitive Intelligence</h2>
                  <div className="team-badge">Strategic insights</div>
                </div>
              </div>
              <p className="team-description">
                Monitor competitor activities, product launches, and strategic positioning in real-time. Stay one step ahead with comprehensive competitive intelligence.
              </p>
              <div className="team-features">
                <h4>Key Capabilities:</h4>
                <ul>
                  <li>Competitor activity tracking</li>
                  <li>Product launch monitoring</li>
                  <li>Market positioning analysis</li>
                  <li>Strategic move detection</li>
                  <li>Competitive benchmarking</li>
                </ul>
              </div>
              <div className="team-sources">
                <h4>Data Sources:</h4>
                <p>The Verge, Product Hunt, TechRadar, Industry Publications</p>
              </div>
            </div>

            <div className="team-detail-card team-researcher">
              <div className="team-header">
                <div className="team-icon-large">🔬</div>
                <div>
                  <h2>Research Team</h2>
                  <div className="team-badge">Innovation radar</div>
                </div>
              </div>
              <p className="team-description">
                Track emerging technologies, academic research, and technical innovations across disciplines. Discover breakthrough technologies before they become mainstream.
              </p>
              <div className="team-features">
                <h4>Key Capabilities:</h4>
                <ul>
                  <li>Academic paper tracking</li>
                  <li>Technology trend analysis</li>
                  <li>Innovation scouting</li>
                  <li>Research breakthrough alerts</li>
                  <li>Technical patent monitoring</li>
                </ul>
              </div>
              <div className="team-sources">
                <h4>Data Sources:</h4>
                <p>ArXiv, MIT Technology Review, Ars Technica, Hacker News, Academic Journals</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Teams;
