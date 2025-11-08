import React, { useState, useEffect } from 'react';
import './PeersNewsroom.css';

function PeersNewsroom() {
  const [quarterlyReports, setQuarterlyReports] = useState([]);
  const [capitalMarkets, setCapitalMarkets] = useState([]);
  const [executiveSpeeches, setExecutiveSpeeches] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Analysis states
  const [transcriptAnalysis, setTranscriptAnalysis] = useState(null);
  const [toneAnalysis, setToneAnalysis] = useState(null);
  const [analyzingTranscript, setAnalyzingTranscript] = useState(false);
  const [analyzingTone, setAnalyzingTone] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  const [showToneModal, setShowToneModal] = useState(false);
  
  // Full report states
  const [fullReport, setFullReport] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  useEffect(() => {
    fetchPeersData();
  }, []);

  const fetchPeersData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API calls
      // const quarterlyResponse = await fetch('/api/peers/quarterly-reports');
      // const capitalResponse = await fetch('/api/peers/capital-markets');
      // const speechesResponse = await fetch('/api/peers/executive-speeches');
      // const analysisResponse = await fetch('/api/peers/analysis');

      // Mock data for now
      setQuarterlyReports([
        {
          id: 1,
          company: 'Apple Inc.',
          quarter: 'Q3 2024',
          title: 'Apple Reports Third Quarter Results',
          date: '2024-11-01',
          keyMetrics: { revenue: '$94.9B', eps: '$1.64', growth: '+5.5%' },
          highlights: ['Services revenue up 14%', 'iPhone sales strong in China', 'AI initiatives progressing'],
          tone: 'positive',
          authority: 9.2
        },
        {
          id: 2,
          company: 'Microsoft Corporation',
          quarter: 'Q3 2024',
          title: 'Microsoft Q3 FY2024 Earnings',
          date: '2024-10-22',
          keyMetrics: { revenue: '$65.6B', eps: '$3.30', growth: '+15.7%' },
          highlights: ['Azure revenue up 31%', 'AI investments paying off', 'Gaming division strong'],
          tone: 'positive',
          authority: 9.5
        }
      ]);

      setCapitalMarkets([
        {
          id: 1,
          title: 'Fed Signals Potential Rate Cuts in 2025',
          source: 'Bloomberg',
          date: '2024-11-08',
          summary: 'Federal Reserve officials indicate possibility of interest rate reductions next year amid cooling inflation',
          impact: 'high',
          sentiment: 'neutral',
          topics: ['monetary policy', 'interest rates', 'inflation']
        },
        {
          id: 2,
          title: 'Tech Sector Shows Resilience in Q3 Earnings',
          source: 'CNBC',
          date: '2024-11-07',
          summary: 'Major tech companies report better-than-expected earnings, driving market optimism',
          impact: 'medium',
          sentiment: 'positive',
          topics: ['earnings', 'tech sector', 'market sentiment']
        }
      ]);

      setExecutiveSpeeches([
        {
          id: 1,
          speaker: 'Satya Nadella',
          company: 'Microsoft',
          title: 'Keynote at Microsoft Ignite 2024',
          date: '2024-11-05',
          topics: ['AI transformation', 'cloud computing', 'productivity'],
          keyQuotes: ['AI is the most transformative technology of our time', 'Every company will become an AI company'],
          tone: 'optimistic',
          authority: 9.8,
          transcript: `Thank you everyone for joining us today. I'm excited to share Microsoft's vision for the future of AI and cloud computing. AI is the most transformative technology of our time, and every company will become an AI company. We're seeing unprecedented innovation in this space, and Microsoft is committed to leading this transformation. Our Azure AI platform is helping businesses of all sizes harness the power of artificial intelligence to drive productivity and innovation. The future belongs to those who embrace AI responsibly and ethically.`
        },
        {
          id: 2,
          speaker: 'Tim Cook',
          company: 'Apple',
          title: 'Apple Privacy & Security Event',
          date: '2024-10-28',
          topics: ['privacy', 'AI integration', 'services growth'],
          keyQuotes: ['Privacy is a fundamental human right', 'AI will enhance user experience without compromising privacy'],
          tone: 'confident',
          authority: 9.6,
          transcript: `Good afternoon, everyone. Today, I'm proud to announce Apple's latest advancements in privacy and AI integration. Privacy is a fundamental human right, and it's at the core of everything we do at Apple. As we integrate AI capabilities into our products, we're doing so in a way that respects and protects user privacy. Our new AI features will enhance the user experience without compromising the security and privacy that our customers expect. We're committed to building technology that empowers people while safeguarding their personal information.`
        }
      ]);

      setAnalysis({
        topTopics: [
          { topic: 'AI & Machine Learning', frequency: 85, trend: 'up', sentiment: 0.7 },
          { topic: 'Cloud Computing', frequency: 72, trend: 'up', sentiment: 0.8 },
          { topic: 'Privacy & Security', frequency: 58, trend: 'stable', sentiment: 0.6 },
          { topic: 'Economic Growth', frequency: 45, trend: 'down', sentiment: 0.3 }
        ],
        toneDistribution: {
          positive: 65,
          neutral: 25,
          negative: 10
        },
        authorityScores: {
          average: 8.7,
          highest: 'Microsoft CEO',
          lowest: 'Small Cap CFO'
        },
        recommendedLanes: [
          {
            lane: 'AI Transformation',
            priority: 'high',
            rationale: '85% of content mentions AI, strong positive sentiment',
            contentIdeas: ['AI adoption case studies', 'Executive AI strategies', 'Technology partnerships']
          },
          {
            lane: 'Cloud Migration',
            priority: 'high',
            rationale: '72% frequency with upward trend',
            contentIdeas: ['Cloud ROI stories', 'Migration best practices', 'Hybrid cloud solutions']
          },
          {
            lane: 'Privacy-First Innovation',
            priority: 'medium',
            rationale: 'Growing regulatory focus, positive executive messaging',
            contentIdeas: ['Privacy compliance guides', 'Secure AI frameworks', 'Data governance']
          }
        ]
      });

    } catch (error) {
      console.error('Error fetching peers data:', error);
    } finally {
      setLoading(false);
    }
  };

  // ChatGPT Analysis Functions
  const analyzeTranscript = async (speech) => {
    try {
      setAnalyzingTranscript(true);
      setTranscriptAnalysis(null);

      const response = await fetch('/api/peers/analyze-transcript', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          speech_id: speech.id.toString(),
          transcript: speech.transcript,
          company: speech.company,
          speaker: speech.speaker
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze transcript');
      }

      const analysis = await response.json();
      setTranscriptAnalysis(analysis);
      setShowTranscriptModal(true);
    } catch (error) {
      console.error('Error analyzing transcript:', error);
      alert('Failed to analyze transcript. Please try again.');
    } finally {
      setAnalyzingTranscript(false);
    }
  };

  const analyzeTone = async (speech) => {
    try {
      setAnalyzingTone(true);
      setToneAnalysis(null);

      const response = await fetch('/api/peers/analyze-tone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          speech_id: speech.id.toString(),
          transcript: speech.transcript,
          company: speech.company,
          speaker: speech.speaker
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze tone');
      }

      const analysis = await response.json();
      setToneAnalysis(analysis);
      setShowToneModal(true);
    } catch (error) {
      console.error('Error analyzing tone:', error);
      alert('Failed to analyze tone. Please try again.');
    } finally {
      setAnalyzingTone(false);
    }
  };

  const closeTranscriptModal = () => {
    setShowTranscriptModal(false);
    setTranscriptAnalysis(null);
  };

  const closeToneModal = () => {
    setShowToneModal(false);
    setToneAnalysis(null);
  };

  // Generate Full Company Report
  const generateFullReport = async (report) => {
    try {
      setGeneratingReport(true);
      setFullReport(null);

      const response = await fetch('/api/peers/generate-full-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company: report.company,
          quarter: report.quarter,
          report_data: report
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate full report');
      }

      const reportData = await response.json();
      setFullReport(reportData);
      setShowReportModal(true);
    } catch (error) {
      console.error('Error generating full report:', error);
      alert('Failed to generate full report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };

  const closeReportModal = () => {
    setShowReportModal(false);
    setFullReport(null);
  };

  const getToneColor = (tone) => {
    switch (tone) {
      case 'positive': return '#10b981';
      case 'neutral': return '#6b7280';
      case 'negative': return '#ef4444';
      case 'optimistic': return '#3b82f6';
      case 'confident': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading Peers Newsroom...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Peers Newsroom</h1>
          <p className="page-subtitle">
            Monitor quarterly reports, capital markets updates, and executive communications to identify emerging trends and content opportunities
          </p>
        </div>
      </section>

      {/* Navigation Tabs */}
      <section className="section">
        <div className="section-content">
          <div className="peers-tabs">
            <button
              className={`peers-tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`peers-tab ${activeTab === 'quarterly' ? 'active' : ''}`}
              onClick={() => setActiveTab('quarterly')}
            >
              Quarterly Reports
            </button>
            <button
              className={`peers-tab ${activeTab === 'markets' ? 'active' : ''}`}
              onClick={() => setActiveTab('markets')}
            >
              Capital Markets
            </button>
            <button
              className={`peers-tab ${activeTab === 'speeches' ? 'active' : ''}`}
              onClick={() => setActiveTab('speeches')}
            >
              Executive Speeches
            </button>
            <button
              className={`peers-tab ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              Analysis & Insights
            </button>
          </div>
        </div>
      </section>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <section className="section">
          <div className="section-content">
            <div className="overview-grid">
              <div className="overview-card">
                <h3>Latest Quarterly Reports</h3>
                <div className="overview-list">
                  {quarterlyReports.slice(0, 3).map(report => (
                    <div key={report.id} className="overview-item">
                      <div className="overview-item-header">
                        <span className="company-name">{report.company}</span>
                        <span className="quarter-badge">{report.quarter}</span>
                      </div>
                      <p className="overview-item-title">{report.title}</p>
                      <div className="overview-metrics">
                        <span className="metric">Revenue: {report.keyMetrics.revenue}</span>
                        <span className="metric">EPS: {report.keyMetrics.eps}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="overview-card">
                <h3>Capital Markets Updates</h3>
                <div className="overview-list">
                  {capitalMarkets.slice(0, 3).map(update => (
                    <div key={update.id} className="overview-item">
                      <div className="overview-item-header">
                        <span className="source-name">{update.source}</span>
                        <span className={`impact-badge ${update.impact}`}>{update.impact}</span>
                      </div>
                      <p className="overview-item-title">{update.title}</p>
                      <p className="overview-summary">{update.summary}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="overview-card">
                <h3>Executive Communications</h3>
                <div className="overview-list">
                  {executiveSpeeches.slice(0, 3).map(speech => (
                    <div key={speech.id} className="overview-item">
                      <div className="overview-item-header">
                        <span className="speaker-name">{speech.speaker}</span>
                        <span className="company-name">{speech.company}</span>
                      </div>
                      <p className="overview-item-title">{speech.title}</p>
                      <div className="speech-topics">
                        {speech.topics.slice(0, 2).map(topic => (
                          <span key={topic} className="topic-tag">{topic}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Quarterly Reports Tab */}
      {activeTab === 'quarterly' && (
        <section className="section">
          <div className="section-content">
            <div className="section-header">
              <h2 className="section-title">Quarterly Reports</h2>
              <p className="section-description">Latest earnings reports and financial results from peer companies</p>
            </div>

            <div className="reports-grid">
              {quarterlyReports.map(report => (
                <div key={report.id} className="report-card">
                  <div className="report-header">
                    <div className="report-company">
                      <h3>{report.company}</h3>
                      <span className="report-quarter">{report.quarter}</span>
                    </div>
                    <div className="report-meta">
                      <span className="report-date">{new Date(report.date).toLocaleDateString()}</span>
                      <span className={`tone-indicator ${report.tone}`} style={{ backgroundColor: getToneColor(report.tone) }}>
                        {report.tone}
                      </span>
                    </div>
                  </div>

                  <h4 className="report-title">{report.title}</h4>

                  <div className="key-metrics">
                    <div className="metric-item">
                      <span className="metric-label">Revenue</span>
                      <span className="metric-value">{report.keyMetrics.revenue}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">EPS</span>
                      <span className="metric-value">{report.keyMetrics.eps}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Growth</span>
                      <span className="metric-value">{report.keyMetrics.growth}</span>
                    </div>
                  </div>

                  <div className="report-highlights">
                    <h5>Key Highlights</h5>
                    <ul>
                      {report.highlights.map((highlight, index) => (
                        <li key={index}>{highlight}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="report-footer">
                    <div className="authority-score">
                      <span>Authority Score: {report.authority}/10</span>
                    </div>
                    <button 
                      className="btn-secondary-small"
                      onClick={() => generateFullReport(report)}
                      disabled={generatingReport}
                    >
                      {generatingReport ? 'Generating...' : 'View Full Report'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Capital Markets Tab */}
      {activeTab === 'markets' && (
        <section className="section">
          <div className="section-content">
            <div className="section-header">
              <h2 className="section-title">Capital Markets Updates</h2>
              <p className="section-description">Market news, analyst reports, and economic indicators</p>
            </div>

            <div className="markets-list">
              {capitalMarkets.map(update => (
                <div key={update.id} className="market-card">
                  <div className="market-header">
                    <div className="market-title-section">
                      <h3>{update.title}</h3>
                      <div className="market-meta">
                        <span className="market-source">{update.source}</span>
                        <span className="market-date">{new Date(update.date).toLocaleDateString()}</span>
                        <span className={`impact-indicator ${update.impact}`} style={{ backgroundColor: getImpactColor(update.impact) }}>
                          {update.impact} impact
                        </span>
                      </div>
                    </div>
                    <div className="market-sentiment">
                      <span className={`sentiment-badge ${update.sentiment}`}>
                        {update.sentiment}
                      </span>
                    </div>
                  </div>

                  <p className="market-summary">{update.summary}</p>

                  <div className="market-topics">
                    {update.topics.map(topic => (
                      <span key={topic} className="topic-tag">{topic}</span>
                    ))}
                  </div>

                  <div className="market-actions">
                    <button className="btn-secondary-small">Read More</button>
                    <button className="btn-outline-small">Analyze</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Executive Speeches Tab */}
      {activeTab === 'speeches' && (
        <section className="section">
          <div className="section-content">
            <div className="section-header">
              <h2 className="section-title">Executive Speeches & Communications</h2>
              <p className="section-description">Key messages from CEOs, CFOs, and other executives</p>
            </div>

            <div className="speeches-grid">
              {executiveSpeeches.map(speech => (
                <div key={speech.id} className="speech-card">
                  <div className="speech-header">
                    <div className="speaker-info">
                      <h3>{speech.speaker}</h3>
                      <span className="speaker-company">{speech.company}</span>
                    </div>
                    <div className="speech-meta">
                      <span className="speech-date">{new Date(speech.date).toLocaleDateString()}</span>
                      <span className={`tone-indicator ${speech.tone}`} style={{ backgroundColor: getToneColor(speech.tone) }}>
                        {speech.tone}
                      </span>
                    </div>
                  </div>

                  <h4 className="speech-title">{speech.title}</h4>

                  <div className="speech-topics">
                    {speech.topics.map(topic => (
                      <span key={topic} className="topic-tag">{topic}</span>
                    ))}
                  </div>

                  <div className="key-quotes">
                    <h5>Key Quotes</h5>
                    <ul>
                      {speech.keyQuotes.map((quote, index) => (
                        <li key={index} className="quote-item">&ldquo;{quote}&rdquo;</li>
                      ))}
                    </ul>
                  </div>

                  <div className="speech-footer">
                    <div className="authority-score">
                      <span>Authority Score: {speech.authority}/10</span>
                    </div>
                    <div className="speech-actions">
                      <button 
                        className="btn-secondary-small"
                        onClick={() => analyzeTranscript(speech)}
                        disabled={analyzingTranscript}
                      >
                        {analyzingTranscript ? 'Analyzing...' : 'View Transcript'}
                      </button>
                      <button 
                        className="btn-outline-small"
                        onClick={() => analyzeTone(speech)}
                        disabled={analyzingTone}
                      >
                        {analyzingTone ? 'Analyzing...' : 'Analyze Tone'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Analysis & Insights Tab */}
      {activeTab === 'analysis' && analysis && (
        <section className="section">
          <div className="section-content">
            <div className="section-header">
              <h2 className="section-title">Analysis & Content Strategy</h2>
              <p className="section-description">AI-powered insights to guide your content and communication strategy</p>
            </div>

            <div className="analysis-grid">
              {/* Top Topics */}
              <div className="analysis-card">
                <h3>Top Topics & Trends</h3>
                <div className="topics-list">
                  {analysis.topTopics.map((topic, index) => (
                    <div key={index} className="topic-item">
                      <div className="topic-header">
                        <span className="topic-name">{topic.topic}</span>
                        <div className="topic-metrics">
                          <span className="topic-frequency">{topic.frequency}%</span>
                          <span className={`trend-indicator ${topic.trend}`}>
                            {topic.trend === 'up' ? '↗' : topic.trend === 'down' ? '↘' : '→'}
                          </span>
                        </div>
                      </div>
                      <div className="sentiment-bar">
                        <div
                          className="sentiment-fill"
                          style={{
                            width: `${(topic.sentiment + 1) * 50}%`,
                            backgroundColor: topic.sentiment > 0 ? '#10b981' : '#ef4444'
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tone Distribution */}
              <div className="analysis-card">
                <h3>Overall Tone Distribution</h3>
                <div className="tone-chart">
                  <div className="tone-bars">
                    <div className="tone-bar">
                      <div className="tone-label">Positive</div>
                      <div className="tone-fill positive" style={{ width: `${analysis.toneDistribution.positive}%` }}>
                        {analysis.toneDistribution.positive}%
                      </div>
                    </div>
                    <div className="tone-bar">
                      <div className="tone-label">Neutral</div>
                      <div className="tone-fill neutral" style={{ width: `${analysis.toneDistribution.neutral}%` }}>
                        {analysis.toneDistribution.neutral}%
                      </div>
                    </div>
                    <div className="tone-bar">
                      <div className="tone-label">Negative</div>
                      <div className="tone-fill negative" style={{ width: `${analysis.toneDistribution.negative}%` }}>
                        {analysis.toneDistribution.negative}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Authority Scores */}
              <div className="analysis-card">
                <h3>Authority Analysis</h3>
                <div className="authority-metrics">
                  <div className="authority-item">
                    <span className="authority-label">Average Score</span>
                    <span className="authority-value">{analysis.authorityScores.average}/10</span>
                  </div>
                  <div className="authority-item">
                    <span className="authority-label">Highest Authority</span>
                    <span className="authority-value">{analysis.authorityScores.highest}</span>
                  </div>
                  <div className="authority-item">
                    <span className="authority-label">Lowest Authority</span>
                    <span className="authority-value">{analysis.authorityScores.lowest}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommended Content Lanes */}
            <div className="content-lanes-section">
              <h3>Recommended Content Lanes</h3>
              <div className="content-lanes-grid">
                {analysis.recommendedLanes.map((lane, index) => (
                  <div key={index} className={`content-lane-card ${lane.priority}`}>
                    <div className="lane-header">
                      <h4>{lane.lane}</h4>
                      <span className={`priority-badge ${lane.priority}`}>{lane.priority} priority</span>
                    </div>
                    <p className="lane-rationale">{lane.rationale}</p>
                    <div className="lane-ideas">
                      <h5>Content Ideas:</h5>
                      <ul>
                        {lane.contentIdeas.map((idea, ideaIndex) => (
                          <li key={ideaIndex}>{idea}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Transcript Analysis Modal */}
      {showTranscriptModal && transcriptAnalysis && (
        <div className="modal-overlay" onClick={closeTranscriptModal}>
          <div className="modal-content analysis-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Transcript Analysis - {transcriptAnalysis.company}</h3>
              <button className="modal-close" onClick={closeTranscriptModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="analysis-summary">
                <h4>Summary</h4>
                <p>{transcriptAnalysis.summary}</p>
              </div>

              <div className="analysis-section">
                <h4>Key Themes</h4>
                <div className="themes-list">
                  {transcriptAnalysis.keyThemes?.map((theme, index) => (
                    <span key={index} className="theme-tag">{theme}</span>
                  ))}
                </div>
              </div>

              <div className="analysis-section">
                <h4>Strategic Insights</h4>
                <ul>
                  {transcriptAnalysis.strategicInsights?.map((insight, index) => (
                    <li key={index}>{insight}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Financial Highlights</h4>
                <ul>
                  {transcriptAnalysis.financialHighlights?.map((highlight, index) => (
                    <li key={index}>{highlight}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Risk Factors</h4>
                <ul>
                  {transcriptAnalysis.riskFactors?.map((risk, index) => (
                    <li key={index}>{risk}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Market Context</h4>
                <p>{transcriptAnalysis.marketContext}</p>
              </div>

              <div className="analysis-section">
                <h4>Future Outlook</h4>
                <p>{transcriptAnalysis.futureOutlook}</p>
              </div>

              <div className="analysis-meta">
                <span className={`sentiment-badge ${transcriptAnalysis.sentiment}`}>
                  Overall Sentiment: {transcriptAnalysis.sentiment}
                </span>
                <span className="confidence-score">
                  Confidence: {Math.round(transcriptAnalysis.confidence * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tone Analysis Modal */}
      {showToneModal && toneAnalysis && (
        <div className="modal-overlay" onClick={closeToneModal}>
          <div className="modal-content analysis-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Tone Analysis - {toneAnalysis.company}</h3>
              <button className="modal-close" onClick={closeToneModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="analysis-summary">
                <h4>Overall Assessment</h4>
                <p>{toneAnalysis.toneSummary}</p>
              </div>

              <div className="analysis-section">
                <h4>Sentiment Analysis</h4>
                <div className="sentiment-metrics">
                  <div className="sentiment-item">
                    <span>Overall Sentiment:</span>
                    <span className={`sentiment-badge ${toneAnalysis.overallSentiment}`}>
                      {toneAnalysis.overallSentiment}
                    </span>
                  </div>
                  <div className="sentiment-item">
                    <span>Sentiment Score:</span>
                    <span>{toneAnalysis.sentimentScore?.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="analysis-section">
                <h4>Emotional Indicators</h4>
                <div className="emotional-indicators">
                  <div className="indicator-item">
                    <span>Confidence:</span>
                    <div className="indicator-bar">
                      <div 
                        className="indicator-fill" 
                        style={{ width: `${toneAnalysis.emotionalIndicators?.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round(toneAnalysis.emotionalIndicators?.confidence * 100)}%</span>
                  </div>
                  <div className="indicator-item">
                    <span>Optimism:</span>
                    <div className="indicator-bar">
                      <div 
                        className="indicator-fill" 
                        style={{ width: `${toneAnalysis.emotionalIndicators?.optimism * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round(toneAnalysis.emotionalIndicators?.optimism * 100)}%</span>
                  </div>
                  <div className="indicator-item">
                    <span>Caution:</span>
                    <div className="indicator-bar">
                      <div 
                        className="indicator-fill" 
                        style={{ width: `${toneAnalysis.emotionalIndicators?.caution * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round(toneAnalysis.emotionalIndicators?.caution * 100)}%</span>
                  </div>
                  <div className="indicator-item">
                    <span>Concern:</span>
                    <div className="indicator-bar">
                      <div 
                        className="indicator-fill" 
                        style={{ width: `${toneAnalysis.emotionalIndicators?.concern * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round(toneAnalysis.emotionalIndicators?.concern * 100)}%</span>
                  </div>
                </div>
              </div>

              <div className="analysis-section">
                <h4>Communication Style</h4>
                <span className="style-badge">{toneAnalysis.communicationStyle}</span>
              </div>

              <div className="analysis-section">
                <h4>Key Emotional Triggers</h4>
                <ul>
                  {toneAnalysis.keyEmotionalTriggers?.map((trigger, index) => (
                    <li key={index}>{trigger}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Audience Engagement</h4>
                <p>{toneAnalysis.audienceEngagement}</p>
              </div>

              <div className="analysis-meta">
                <span className="confidence-score">
                  Speaker Confidence: {Math.round(toneAnalysis.confidenceLevel * 100)}%
                </span>
                <span className="analysis-confidence">
                  Analysis Confidence: {Math.round(toneAnalysis.confidence * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Report Modal */}
      {showReportModal && fullReport && (
        <div className="modal-overlay" onClick={closeReportModal}>
          <div className="modal-content report-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Full Company Report - {fullReport.company}</h3>
              <button className="modal-close" onClick={closeReportModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="report-meta-section">
                <div className="report-meta-item">
                  <span className="meta-label">Report Period:</span>
                  <span className="meta-value">{fullReport.quarter}</span>
                </div>
                <div className="report-meta-item">
                  <span className="meta-label">Generated:</span>
                  <span className="meta-value">{new Date(fullReport.generated_at).toLocaleString()}</span>
                </div>
                <div className="report-meta-item">
                  <span className="meta-label">Analysis Confidence:</span>
                  <span className="meta-value">{Math.round(fullReport.confidence * 100)}%</span>
                </div>
              </div>

              <div className="report-section">
                <h4>Executive Summary</h4>
                <p>{fullReport.executiveSummary}</p>
              </div>

              <div className="report-section">
                <h4>Financial Performance Analysis</h4>
                <div className="financial-analysis">
                  <div className="analysis-subsection">
                    <h5>Revenue Analysis</h5>
                    <p>{fullReport.financialAnalysis.revenueAnalysis}</p>
                  </div>
                  <div className="analysis-subsection">
                    <h5>Profitability Metrics</h5>
                    <p>{fullReport.financialAnalysis.profitabilityAnalysis}</p>
                  </div>
                  <div className="analysis-subsection">
                    <h5>Growth Trends</h5>
                    <p>{fullReport.financialAnalysis.growthAnalysis}</p>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <h4>Balance Sheet Analysis</h4>
                <p>{fullReport.balanceSheetAnalysis}</p>
              </div>

              <div className="report-section">
                <h4>Cash Flow Analysis</h4>
                <p>{fullReport.cashFlowAnalysis}</p>
              </div>

              <div className="report-section">
                <h4>Key Ratios & Metrics</h4>
                <div className="ratios-grid">
                  {fullReport.keyRatios.map((ratio, index) => (
                    <div key={index} className="ratio-item">
                      <span className="ratio-name">{ratio.name}</span>
                      <span className="ratio-value">{ratio.value}</span>
                      <span className="ratio-interpretation">{ratio.interpretation}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="report-section">
                <h4>Industry Comparison</h4>
                <p>{fullReport.industryComparison}</p>
              </div>

              <div className="report-section">
                <h4>Risk Assessment</h4>
                <div className="risk-assessment">
                  <div className="risk-item">
                    <h5>Financial Risks</h5>
                    <ul>
                      {fullReport.riskAssessment.financialRisks.map((risk, index) => (
                        <li key={index}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="risk-item">
                    <h5>Operational Risks</h5>
                    <ul>
                      {fullReport.riskAssessment.operationalRisks.map((risk, index) => (
                        <li key={index}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="risk-item">
                    <h5>Market Risks</h5>
                    <ul>
                      {fullReport.riskAssessment.marketRisks.map((risk, index) => (
                        <li key={index}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <h4>Investment Recommendation</h4>
                <div className={`recommendation-box ${fullReport.investmentRecommendation.rating.toLowerCase()}`}>
                  <h5>{fullReport.investmentRecommendation.rating}</h5>
                  <p>{fullReport.investmentRecommendation.rationale}</p>
                  <div className="recommendation-details">
                    <span>Target Price: {fullReport.investmentRecommendation.targetPrice}</span>
                    <span>Time Horizon: {fullReport.investmentRecommendation.timeHorizon}</span>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <h4>Forward Outlook</h4>
                <p>{fullReport.forwardOutlook}</p>
              </div>

              <div className="report-disclaimer">
                <p><strong>Disclaimer:</strong> This AI-generated analysis is for informational purposes only and should not be considered as financial advice. Always consult with qualified financial professionals before making investment decisions.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PeersNewsroom;