import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './ReputationMap.css';

function ReputationMap() {
  // Initial mock data for immediate map loading
  const initialMockData = [
    {
      id: 1,
      country: 'United States',
      region: 'North America',
      coordinates: [39.8283, -98.5795],
      riskType: 'regulatory',
      severity: 'high',
      title: 'SEC Investigation into Tech Company',
      description: 'Ongoing SEC investigation into accounting practices',
      impact: 'High regulatory scrutiny in tech sector',
      sources: ['SEC Filings', 'Bloomberg', 'Reuters'],
      sentiment: -0.8,
      trend: 'increasing',
      lastUpdated: '2024-11-08',
      esgScore: 65,
      controversyLevel: 'high',
      regulatoryActions: 3
    },
    {
      id: 2,
      country: 'United Kingdom',
      region: 'Europe',
      coordinates: [55.3781, -3.4360],
      riskType: 'reputational',
      severity: 'medium',
      title: 'Data Privacy Concerns',
      description: 'Customer data breach affecting millions',
      impact: 'Medium reputational damage in EU market',
      sources: ['BBC', 'Financial Times', 'ICO'],
      sentiment: -0.6,
      trend: 'stable',
      lastUpdated: '2024-11-07',
      esgScore: 72,
      controversyLevel: 'medium',
      regulatoryActions: 1
    },
    {
      id: 3,
      country: 'Germany',
      region: 'Europe',
      coordinates: [51.1657, 10.4515],
      riskType: 'operational',
      severity: 'low',
      title: 'Supply Chain Disruption',
      description: 'Temporary production halt due to component shortage',
      impact: 'Low operational impact, resolved quickly',
      sources: ['Reuters', 'DW News'],
      sentiment: -0.3,
      trend: 'decreasing',
      lastUpdated: '2024-11-06',
      esgScore: 78,
      controversyLevel: 'low',
      regulatoryActions: 0
    },
    {
      id: 4,
      country: 'Japan',
      region: 'Asia',
      coordinates: [36.2048, 138.2529],
      riskType: 'opportunity',
      severity: 'high',
      title: 'Market Expansion Opportunity',
      description: 'Growing demand for sustainable products in Asia-Pacific',
      impact: 'High growth potential in emerging markets',
      sources: ['Nikkei', 'Bloomberg', 'Market Research'],
      sentiment: 0.7,
      trend: 'increasing',
      lastUpdated: '2024-11-08',
      esgScore: 85,
      controversyLevel: 'low',
      regulatoryActions: 0
    },
    {
      id: 5,
      country: 'Australia',
      region: 'Oceania',
      coordinates: [-25.2744, 133.7751],
      riskType: 'regulatory',
      severity: 'medium',
      title: 'Environmental Compliance Review',
      description: 'ASIC reviewing environmental disclosure practices',
      impact: 'Medium regulatory oversight in mining sector',
      sources: ['ASIC', 'Sydney Morning Herald'],
      sentiment: -0.4,
      trend: 'stable',
      lastUpdated: '2024-11-05',
      esgScore: 70,
      controversyLevel: 'medium',
      regulatoryActions: 2
    },
    {
      id: 6,
      country: 'Canada',
      region: 'North America',
      coordinates: [56.1304, -106.3468],
      riskType: 'reputational',
      severity: 'high',
      title: 'Executive Compensation Controversy',
      description: 'Public backlash against executive pay packages',
      impact: 'High reputational risk in Canadian market',
      sources: ['Globe and Mail', 'CBC News'],
      sentiment: -0.9,
      trend: 'increasing',
      lastUpdated: '2024-11-08',
      esgScore: 68,
      controversyLevel: 'high',
      regulatoryActions: 0
    },
    {
      id: 7,
      country: 'Brazil',
      region: 'South America',
      coordinates: [-14.2350, -51.9253],
      riskType: 'operational',
      severity: 'medium',
      title: 'Labor Relations Issues',
      description: 'Union disputes affecting production facilities',
      impact: 'Medium operational disruption in South America',
      sources: ['Reuters', 'Folha de S.Paulo'],
      sentiment: -0.5,
      trend: 'stable',
      lastUpdated: '2024-11-07',
      esgScore: 75,
      controversyLevel: 'medium',
      regulatoryActions: 1
    },
    {
      id: 8,
      country: 'India',
      region: 'Asia',
      coordinates: [20.5937, 78.9629],
      riskType: 'opportunity',
      severity: 'medium',
      title: 'Digital Transformation Initiative',
      description: 'Government push for digital adoption creates market opportunities',
      impact: 'Medium growth opportunity in digital services',
      sources: ['Economic Times', 'Business Standard'],
      sentiment: 0.6,
      trend: 'increasing',
      lastUpdated: '2024-11-06',
      esgScore: 80,
      controversyLevel: 'low',
      regulatoryActions: 0
    },
    {
      id: 9,
      country: 'South Africa',
      region: 'Africa',
      coordinates: [-30.5595, 22.9375],
      riskType: 'regulatory',
      severity: 'low',
      title: 'Mining License Renewal',
      description: 'Routine regulatory compliance for mining operations',
      impact: 'Low regulatory oversight, standard procedure',
      sources: ['Mining Weekly', 'Business Day'],
      sentiment: -0.2,
      trend: 'stable',
      lastUpdated: '2024-11-04',
      esgScore: 73,
      controversyLevel: 'low',
      regulatoryActions: 1
    },
    {
      id: 10,
      country: 'Singapore',
      region: 'Asia',
      coordinates: [1.3521, 103.8198],
      riskType: 'reputational',
      severity: 'medium',
      title: 'Corporate Governance Review',
      description: 'Independent review of board practices recommended',
      impact: 'Medium reputational concern in financial hub',
      sources: ['Straits Times', 'Bloomberg'],
      sentiment: -0.4,
      trend: 'decreasing',
      lastUpdated: '2024-11-03',
      esgScore: 82,
      controversyLevel: 'medium',
      regulatoryActions: 0
    },
    {
      id: 11,
      country: 'Netherlands',
      region: 'Europe',
      coordinates: [52.1326, 5.2913],
      riskType: 'opportunity',
      severity: 'low',
      title: 'Sustainable Finance Growth',
      description: 'Increasing focus on ESG investments in European markets',
      impact: 'Low but growing opportunity in sustainable finance',
      sources: ['Financial Times', 'ING Research'],
      sentiment: 0.3,
      trend: 'increasing',
      lastUpdated: '2024-11-02',
      esgScore: 88,
      controversyLevel: 'low',
      regulatoryActions: 0
    }
  ];

  const [reputationData, setReputationData] = useState(initialMockData);
  const [fetchingAdditionalData, setFetchingAdditionalData] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [filters, setFilters] = useState({
    riskType: 'all',
    timeRange: '30d',
    severity: 'all'
  });
  const [mapView, setMapView] = useState('world');

  const fetchReputationData = useCallback(async () => {
    try {
      setFetchingAdditionalData(true);
      // Fetch real data from backend API
      const response = await fetch(`http://localhost:8000/api/reputation/map?riskType=${filters.riskType}&timeRange=${filters.timeRange}&severity=${filters.severity}&region=${filters.region || 'all'}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform backend data to frontend format
      const transformedData = data.data.map(item => ({
        id: item.id,
        country: item.country,
        region: item.region,
        coordinates: item.coordinates,
        riskType: item.riskType,
        severity: item.severity,
        title: item.title,
        description: item.description,
        impact: item.impact,
        sources: item.sources,
        sentiment: item.sentiment,
        trend: item.trend,
        lastUpdated: item.lastUpdated,
        esgScore: item.esgScore,
        controversyLevel: item.controversyLevel,
        regulatoryActions: item.regulatoryActions
      }));
      
      // Add new data points progressively instead of replacing all data
      setReputationData(currentData => {
        // Filter out any existing data points that match the new ones by ID to avoid duplicates
        const existingIds = new Set(currentData.map(item => item.id));
        const newDataPoints = transformedData.filter(item => !existingIds.has(item.id));
        
        // Add new points with a small delay between each to show progressive loading
        if (newDataPoints.length > 0) {
          newDataPoints.forEach((point, index) => {
            setTimeout(() => {
              setReputationData(prevData => [...prevData, point]);
            }, index * 200); // 200ms delay between each point
          });
        }
        
        return currentData;
      });
      
    } catch (error) {
      console.error('Error fetching reputation data:', error);
      // Don't fallback to mock data since we already have initial mock data
    } finally {
      setFetchingAdditionalData(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchReputationData();
  }, [fetchReputationData]);

  const getHeatmapColor = (intensity) => {
    // Create gradient from white (0) to red (1)
    const r = Math.floor(255 * intensity);
    const g = Math.floor(255 * (1 - intensity));
    const b = Math.floor(255 * (1 - intensity));
    return `rgb(${r}, ${g}, ${b})`;
  };

  const getRiskColor = (riskType, severity) => {
    if (riskType === 'opportunity') {
      return severity === 'high' ? '#10b981' : severity === 'medium' ? '#34d399' : '#6ee7b7';
    }

    switch (severity) {
      case 'high': return '#dc2626';
      case 'medium': return '#f59e0b';
      case 'low': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getRiskIcon = (riskType) => {
    switch (riskType) {
      case 'regulatory': return '⚖️';
      case 'reputational': return '📰';
      case 'operational': return '🏭';
      case 'opportunity': return '📈';
      default: return '⚠️';
    }
  };

  const filteredData = reputationData.filter(item => {
    if (filters.riskType !== 'all' && item.riskType !== filters.riskType) return false;
    if (filters.severity !== 'all' && item.severity !== filters.severity) return false;
    return true;
  });

  const riskSummary = {
    total: filteredData.length,
    high: filteredData.filter(d => d.severity === 'high').length,
    medium: filteredData.filter(d => d.severity === 'medium').length,
    low: filteredData.filter(d => d.severity === 'low').length,
    opportunities: filteredData.filter(d => d.riskType === 'opportunity').length
  };

  return (
    <div className="page-container">
      <section className="page-hero">
        <div className="page-hero-content">
          <h1 className="page-title">Reputation Map</h1>
          <p className="page-subtitle">
            Geographic heatmap showing reputation risk intensity across global markets based on source coverage
          </p>
        </div>
      </section>

      {/* Controls Section */}
      <section className="section">
        <div className="section-content">
          <div className="reputation-controls">
            <div className="control-group">
              <label>Risk Type:</label>
              <select
                value={filters.riskType}
                onChange={(e) => setFilters({...filters, riskType: e.target.value})}
                className="filter-select"
              >
                <option value="all">All Types</option>
                <option value="regulatory">Regulatory</option>
                <option value="reputational">Reputational</option>
                <option value="operational">Operational</option>
                <option value="opportunity">Opportunities</option>
              </select>
            </div>

            <div className="control-group">
              <label>Time Range:</label>
              <select
                value={filters.timeRange}
                onChange={(e) => setFilters({...filters, timeRange: e.target.value})}
                className="filter-select"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
            </div>

            <div className="control-group">
              <label>Severity:</label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
                className="filter-select"
              >
                <option value="all">All Levels</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div className="control-group">
              <label>View:</label>
              <select
                value={mapView}
                onChange={(e) => setMapView(e.target.value)}
                className="filter-select"
              >
                <option value="world">World</option>
                <option value="americas">Americas</option>
                <option value="europe">Europe</option>
                <option value="asia">Asia</option>
              </select>
            </div>

            <div className="control-group">
              <button
                onClick={fetchReputationData}
                disabled={fetchingAdditionalData}
                className={`btn-primary-small ${fetchingAdditionalData ? 'loading' : ''}`}
                style={{ marginTop: '20px' }}
              >
                {fetchingAdditionalData ? (
                  <>
                    <div className="loading-spinner-small"></div>
                    Loading Data...
                  </>
                ) : (
                  'Load Latest Data'
                )}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Summary Cards */}
      <section className="section">
        <div className="section-content">
          <div className="summary-grid">
            <div className="summary-card">
              <div className="summary-value">{riskSummary.total}</div>
              <div className="summary-label">Total Issues</div>
            </div>
            <div className="summary-card high">
              <div className="summary-value">{riskSummary.high}</div>
              <div className="summary-label">High Severity</div>
            </div>
            <div className="summary-card medium">
              <div className="summary-value">{riskSummary.medium}</div>
              <div className="summary-label">Medium Severity</div>
            </div>
            <div className="summary-card opportunity">
              <div className="summary-value">{riskSummary.opportunities}</div>
              <div className="summary-label">Opportunities</div>
            </div>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="section">
        <div className="section-content">
          <div className="map-container">
            <div className="map-placeholder">
              <div className="map-header">
                <h3>Global Reputation Risk Heatmap</h3>
                <p>Heatmap visualization showing risk intensity based on source coverage and severity. Click markers for details.</p>
              </div>

              {/* Interactive Leaflet Map */}
              <div className="world-map">
                <MapContainer
                  center={[20, 0]}
                  zoom={1.5}
                  style={{ height: '500px', width: '100%' }}
                  className="leaflet-map"
                  maxBounds={[[-90, -180], [90, 180]]}
                  maxBoundsViscosity={1.0}
                  worldCopyJump={false}
                  noWrap={true}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />

                  {/* Heatmap Overlay */}
                  {filteredData.map((item) => {
                    // Calculate heatmap intensity based on severity and number of sources
                    const baseIntensity = item.severity === 'high' ? 0.8 :
                                        item.severity === 'medium' ? 0.5 : 0.3;
                    const sourceMultiplier = Math.min(item.sources.length / 3, 1); // Max at 3 sources
                    const intensity = Math.min(baseIntensity * (0.5 + sourceMultiplier * 0.5), 1);

                    // Create multiple overlapping circles for heatmap effect
                    const circles = [];
                    const radii = [150000, 120000, 90000, 60000]; // Increased radii for better visibility

                    radii.forEach((radius, index) => {
                      const opacity = intensity * (1 - index * 0.2); // Decreasing opacity for outer circles
                      const color = getHeatmapColor(intensity);

                      circles.push(
                        <Circle
                          key={`${item.id}-${index}`}
                          center={item.coordinates}
                          radius={radius}
                          pathOptions={{
                            color: color,
                            fillColor: color,
                            fillOpacity: opacity,
                            weight: 0, // No border for smoother heatmap
                            stroke: false
                          }}
                          eventHandlers={{
                            click: () => setSelectedRegion(item)
                          }}
                        />
                      );
                    });

                    return circles;
                  })}

                  {/* Risk markers for interaction */}
                  {filteredData.map((item) => {
                    const riskColor = getRiskColor(item.riskType, item.severity);

                    return (
                      <Circle
                        key={`marker-${item.id}`}
                        center={item.coordinates}
                        radius={15000}
                        pathOptions={{
                          color: riskColor,
                          fillColor: riskColor,
                          fillOpacity: 1,
                          weight: 3
                        }}
                        eventHandlers={{
                          click: () => setSelectedRegion(item)
                        }}
                      />
                    );
                  })}
                </MapContainer>

                {/* Legend */}
                <div className="map-legend">
                  <h4>Risk Intensity</h4>
                  <div className="legend-items">
                    <div className="legend-item">
                      <div className="heatmap-gradient"></div>
                      <div className="gradient-labels">
                        <span>Low</span>
                        <span>High</span>
                      </div>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#dc2626' }}></span>
                      <span>High Risk Marker</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#f59e0b' }}></span>
                      <span>Medium Risk Marker</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#6b7280' }}></span>
                      <span>Low Risk Marker</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#10b981' }}></span>
                      <span>Opportunity Marker</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Details Panel */}
            {selectedRegion && (
              <div className="details-panel">
                <div className="details-header">
                  <h3>{selectedRegion.country}</h3>
                  <button
                    className="close-button"
                    onClick={() => setSelectedRegion(null)}
                  >
                    ×
                  </button>
                </div>

                <div className="details-content">
                  <div className="detail-item">
                    <span className="detail-label">Risk Type:</span>
                    <span className={`risk-badge ${selectedRegion.riskType}`}>
                      {getRiskIcon(selectedRegion.riskType)} {selectedRegion.riskType}
                    </span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Severity:</span>
                    <span className={`severity-badge ${selectedRegion.severity}`}>
                      {selectedRegion.severity}
                    </span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Title:</span>
                    <span>{selectedRegion.title}</span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Description:</span>
                    <span>{selectedRegion.description}</span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Impact:</span>
                    <span>{selectedRegion.impact}</span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Sentiment:</span>
                    <div className="sentiment-bar">
                      <div
                        className="sentiment-fill"
                        style={{
                          width: `${((selectedRegion.sentiment + 1) * 50)}%`,
                          backgroundColor: selectedRegion.sentiment > 0 ? '#10b981' : '#ef4444'
                        }}
                      ></div>
                      <span className="sentiment-value">{selectedRegion.sentiment.toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Sources:</span>
                    <div className="sources-list">
                      {selectedRegion.sources.map((source, index) => (
                        <span key={index} className="source-tag">{source}</span>
                      ))}
                    </div>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Last Updated:</span>
                    <span>{new Date(selectedRegion.lastUpdated).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="details-actions">
                  <button className="btn-secondary-small">View Full Report</button>
                  <button className="btn-outline-small">Monitor Region</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Data Sources Section */}
      <section className="section">
        <div className="section-content">
          <div className="section-header">
            <h2 className="section-title">Data Sources</h2>
            <p className="section-description">Comprehensive coverage from global news, regulatory, and industry sources</p>
          </div>

          <div className="sources-grid">
            <div className="source-card">
              <h4>News & Media</h4>
              <ul>
                <li>NewsAPI - Real-time news monitoring</li>
                <li>RSS News Feeds - Major publications</li>
                <li>Wikipedia - Company history & controversies</li>
                <li>Reddit - Community discussions</li>
              </ul>
            </div>

            <div className="source-card">
              <h4>Regulatory & Compliance</h4>
              <ul>
                <li>SEC EDGAR - US company filings</li>
                <li>Companies House - UK registry</li>
                <li>OpenCorporates - Global company data</li>
                <li>BBB - Business accreditation</li>
              </ul>
            </div>

            <div className="source-card">
              <h4>App Store & Reviews</h4>
              <ul>
                <li>Google Play Store - Android apps</li>
                <li>Apple App Store - iOS apps</li>
                <li>Trustpilot - Customer reviews</li>
                <li>WHOIS - Domain registration</li>
              </ul>
            </div>

            <div className="source-card">
              <h4>Open Source & Social</h4>
              <ul>
                <li>GitHub API - Repository activity</li>
                <li>Social Media Presence - Platform monitoring</li>
                <li>Clearbit - Company enrichment</li>
                <li>Hunter.io - Email verification</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default ReputationMap;