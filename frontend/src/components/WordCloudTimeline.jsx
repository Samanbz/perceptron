import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
import './WordCloudTimeline.css';

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Available teams - now fetched from API but with fallback
const DEFAULT_TEAMS = [
  {
    key: 'regulator',
    name: 'Regulatory Team',
  },
  {
    key: 'competitor',
    name: 'Competitive Intelligence',
  },
  {
    key: 'investor',
    name: 'Investment Team',
  },
  {
    key: 'researcher',
    name: 'Research Team',
  },
];

/**
 * ImportanceTrendChart Component
 * Minimal line chart showing importance trend over time
 */
function ImportanceTrendChart({ timeSeries }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current || !timeSeries || timeSeries.length === 0) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const width = chartRef.current.clientWidth - margin.left - margin.right;
    const height = 150 - margin.top - margin.bottom;

    const svg = d3
      .select(chartRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(timeSeries, d => new Date(d.date)))
      .range([0, width]);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(timeSeries, d => d.importance) * 1.2])
      .range([height, 0]);

    // Create line generator
    const line = d3
      .line()
      .x(d => xScale(new Date(d.date)))
      .y(d => yScale(d.importance))
      .curve(d3.curveMonotoneX);

    // Add gradient for area
    const gradient = svg
      .append('defs')
      .append('linearGradient')
      .attr('id', 'importance-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%');

    gradient
      .append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#00a3e0')
      .attr('stop-opacity', 0.3);

    gradient
      .append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#00a3e0')
      .attr('stop-opacity', 0);

    // Add area under the line
    const area = d3
      .area()
      .x(d => xScale(new Date(d.date)))
      .y0(height)
      .y1(d => yScale(d.importance))
      .curve(d3.curveMonotoneX);

    svg
      .append('path')
      .datum(timeSeries)
      .attr('fill', 'url(#importance-gradient)')
      .attr('d', area);

    // Add the line
    svg
      .append('path')
      .datum(timeSeries)
      .attr('fill', 'none')
      .attr('stroke', '#0018a8')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Add dots for data points
    svg
      .selectAll('.dot')
      .data(timeSeries)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(new Date(d.date)))
      .attr('cy', d => yScale(d.importance))
      .attr('r', 3)
      .attr('fill', '#0018a8');

    // Add axes
    const xAxis = d3
      .axisBottom(xScale)
      .ticks(3)
      .tickFormat(d3.timeFormat('%b %d'));

    const yAxis = d3.axisLeft(yScale).ticks(4);

    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis)
      .style('font-size', '10px')
      .style('color', '#666');

    svg
      .append('g')
      .call(yAxis)
      .style('font-size', '10px')
      .style('color', '#666');
  }, [timeSeries]);

  if (!timeSeries || timeSeries.length === 0) {
    return (
      <div className="importance-trend-section">
        <h4>Activity Over Time</h4>
        <p className="no-trend-data">No historical data available</p>
      </div>
    );
  }

  return (
    <div className="importance-trend-section">
      <h4>Activity Over Time</h4>
      <div ref={chartRef} className="importance-chart"></div>
    </div>
  );
}

/**
 * WordCloudTimeline Component
 *
 * Visualizes keyword importance over time with animated transitions.
 * - Word size represents importance score
 * - Word color represents sentiment (green=positive, red=negative, gray=neutral)
 * - Color intensity represents sentiment magnitude
 * - Time slider allows navigation through historical data
 *
 * Domain Context: This is the primary "Weak Signal" visualization component.
 * It surfaces high-importance, low-velocity keywords that might indicate
 * emerging reputational risks before they become mainstream news.
 */
function WordCloudTimeline() {
  const [data, setData] = useState(null);
  const [teams, setTeams] = useState(DEFAULT_TEAMS);
  const [currentDayIndex, setCurrentDayIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const svgRef = useRef(null);
  const playIntervalRef = useRef(null);

  // Generate array of dates for the slider (last 7 days) - memoize to prevent infinite loops
  const dateRange = useMemo(() => {
    const dates = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }
    console.log('[WordCloud] Generated date range:', dates);
    return dates;
  }, []);

  const selectedDate = dateRange[currentDayIndex];

  // Fetch teams from API
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/teams`)
      .then(response => response.json())
      .then(data => {
        if (data.teams && data.teams.length > 0) {
          setTeams(data.teams);
        }
      })
      .catch(err => {
        console.warn('Failed to load teams from API, using defaults:', err);
      });
  }, []);

  // Fetch data for all dates when team changes
  useEffect(() => {
    if (!selectedTeam) {
      console.log('[WordCloud] No team selected');
      return;
    }

    console.log('[WordCloud] Fetching data for team:', selectedTeam);
    console.log('[WordCloud] Date range:', dateRange);

    setLoading(true);
    setError(null);

    // Fetch data for each date in parallel
    const fetchPromises = dateRange.map(date => {
      const url = `${API_BASE_URL}/api/keywords/${selectedTeam}/${date}`;
      console.log('[WordCloud] Fetching:', url);

      return fetch(url)
        .then(response => {
          console.log('[WordCloud] Response for', date, ':', response.status);
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          return response.json();
        })
        .then(jsonData => {
          console.log(
            '[WordCloud] Data for',
            date,
            ':',
            jsonData.total_keywords,
            'keywords'
          );
          return { date, data: jsonData };
        })
        .catch(err => {
          console.warn(`[WordCloud] Failed to fetch data for ${date}:`, err);
          return { date, data: null };
        });
    });

    Promise.all(fetchPromises)
      .then(results => {
        console.log('[WordCloud] All fetch results:', results);

        // Combine all results into a single data object
        // Keywords already have date field from API, so we don't need to add it
        const allKeywords = results
          .filter(r => r.data && r.data.keywords)
          .flatMap(r => r.data.keywords);

        console.log(
          '[WordCloud] Total keywords collected:',
          allKeywords.length
        );
        console.log(
          '[WordCloud] Sample keyword dates:',
          allKeywords.slice(0, 3).map(k => k.date)
        );

        const combinedData = {
          team_key: selectedTeam,
          team_name: results[0]?.data?.team_name || selectedTeam,
          keywords: allKeywords,
          total_keywords: allKeywords.length,
          dateRange: results.map(r => ({
            date: r.date,
            hasData: r.data !== null,
          })),
        };

        console.log('[WordCloud] Setting combined data:', combinedData);
        setData(combinedData);
        setLoading(false);
      })
      .catch(err => {
        console.error('[WordCloud] Error loading data:', err);
        setError(err.message);
        setLoading(false);
      });
  }, [selectedTeam, dateRange]);

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying && data) {
      playIntervalRef.current = setInterval(() => {
        setCurrentDayIndex(prev => {
          if (prev >= dateRange.length - 1) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 1;
        });
      }, 1500); // Change day every 1.5 seconds
    }

    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, [isPlaying, data, dateRange.length]);

  /**
   * Get keywords for the current date index
   */
  const getKeywordsForCurrentDate = useCallback(() => {
    if (!data || !data.keywords) {
      console.log('[WordCloud] getKeywordsForCurrentDate: No data');
      return [];
    }
    const targetDate = selectedDate;

    // Debug: Show unique dates in data
    const uniqueDates = [...new Set(data.keywords.map(kw => kw.date))];
    console.log('[WordCloud] Available dates in data:', uniqueDates);
    console.log('[WordCloud] Looking for date:', targetDate);

    const filtered = data.keywords.filter(kw => kw.date === targetDate);
    console.log('[WordCloud] Keywords for', targetDate, ':', filtered.length);

    if (filtered.length === 0) {
      console.log(
        '[WordCloud] Sample keyword dates:',
        data.keywords
          .slice(0, 5)
          .map(k => ({ keyword: k.keyword, date: k.date }))
      );
    }

    return filtered;
  }, [data, selectedDate]);

  /**
   * Maps sentiment score and magnitude to color
   * Light theme color scheme matching the brand palette
   */
  const getSentimentColor = useCallback(sentiment => {
    const score = sentiment.score;
    const magnitude = sentiment.magnitude;

    // Subtle intensity based on magnitude (0-1 scale)
    const intensity = Math.min(1, magnitude) * 0.6;

    if (score > 0.2) {
      // Positive: Green gradient (#00A876)
      const g = Math.round(168 + 30 * intensity);
      const b = Math.round(118 + 32 * intensity);
      return `rgb(0, ${g}, ${b})`;
    } else if (score < -0.2) {
      // Negative: Orange gradient (#E86A33)
      const r = Math.round(232 + 23 * intensity);
      const g = Math.round(106 + 32 * intensity);
      const b = Math.round(51 + 32 * intensity);
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      // Neutral: Blue-gray gradient
      const r = Math.round(176 + 30 * intensity);
      const g = Math.round(184 + 30 * intensity);
      const b = Math.round(192 + 32 * intensity);
      return `rgb(${r}, ${g}, ${b})`;
    }
  }, []);

  const showTooltip = useCallback((event, d) => {
    const tooltip = d3.select('#word-cloud-tooltip');

    const sentimentLabel =
      d.sentiment.score > 0.2
        ? 'Positive'
        : d.sentiment.score < -0.2
          ? 'Negative'
          : 'Neutral';

    tooltip
      .style('display', 'block')
      .style('left', `${event.pageX + 10}px`)
      .style('top', `${event.pageY - 10}px`).html(`
        <div class="tooltip-header">
          <strong>${d.text}</strong>
        </div>
        <div class="tooltip-content">
          <div class="tooltip-row">
            <span class="tooltip-label">Importance:</span>
            <span class="tooltip-value">${d.importance.toFixed(2)}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Sentiment:</span>
            <span class="tooltip-value">${sentimentLabel} (${d.sentiment.score.toFixed(3)})</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Magnitude:</span>
            <span class="tooltip-value">${d.sentiment.magnitude.toFixed(3)}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Frequency:</span>
            <span class="tooltip-value">${d.metrics.frequency}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Velocity:</span>
            <span class="tooltip-value">${d.metrics.velocity.toFixed(2)}%</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Documents:</span>
            <span class="tooltip-value">${d.metrics.document_count}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Sources:</span>
            <span class="tooltip-value">${d.metrics.source_diversity}</span>
          </div>
        </div>
      `);
  }, []);

  const hideTooltip = useCallback(() => {
    d3.select('#word-cloud-tooltip').style('display', 'none');
  }, []);

  /**
   * Generate time series data from all keyword entries with the same keyword text
   * Shows keyword importance trend over time across all dates
   */
  const getImportanceTimeSeries = useCallback(
    keywordData => {
      if (!keywordData || !data || !data.keywords) return [];

      const keywordText = keywordData.text;

      // Find ALL keyword entries with the same keyword text across all dates
      const allKeywordEntries = data.keywords.filter(
        kw => kw.keyword === keywordText
      );

      if (allKeywordEntries.length === 0) return [];

      // Create time series from the importance values at each date
      const timeSeries = allKeywordEntries
        .map(kw => ({
          date: kw.date,
          importance: kw.importance,
        }))
        .sort((a, b) => new Date(a.date) - new Date(b.date));

      return timeSeries;
    },
    [data]
  );

  // Render word cloud when data or day changes
  useEffect(() => {
    console.log('[WordCloud] Render effect triggered');
    console.log(
      '[WordCloud] Data:',
      data ? `${data.keywords?.length} keywords` : 'null'
    );
    console.log('[WordCloud] SVG ref:', svgRef.current ? 'exists' : 'null');
    console.log('[WordCloud] Current day index:', currentDayIndex);
    console.log('[WordCloud] Selected date:', selectedDate);

    if (!data || !data.keywords || !svgRef.current) {
      console.log('[WordCloud] Skipping render - missing data or ref');
      return;
    }

    // Get keywords for the current date
    const currentDateKeywords = getKeywordsForCurrentDate();
    console.log(
      '[WordCloud] Current date keywords:',
      currentDateKeywords.length
    );

    if (currentDateKeywords.length === 0) {
      console.log('[WordCloud] No keywords for current date, clearing cloud');
      // Clear the word cloud if no keywords for this date
      const svg = d3.select(svgRef.current);
      svg.selectAll('g.word-cloud-group').selectAll('text').remove();
      return;
    }

    // Prepare words for cloud layout - use top 30 keywords for current date
    const words = currentDateKeywords.slice(0, 30).map((kw, idx) => ({
      text: kw.keyword,
      // Scale size by importance (30-100 range)
      size:
        idx === 0
          ? Math.max(18, Math.min(52, kw.importance * 0.52))
          : Math.max(11, Math.min(36, kw.importance * 0.36)),
      importance: kw.importance,
      sentiment: kw.sentiment,
      metrics: kw.metrics,
      documents: kw.documents,
    }));

    console.log('[WordCloud] Rendering', words.length, 'words');

    /**
     * Renders the word cloud using D3 cloud layout with smooth transitions
     */
    const renderWordCloud = words => {
      const svg = d3.select(svgRef.current);
      const width = svgRef.current.clientWidth;
      const height = svgRef.current.clientHeight;

      if (width === 0 || height === 0) {
        console.log('[WordCloud] SVG has no dimensions, skipping render');
        return;
      }

      console.log(
        '[WordCloud] Starting layout calculation for',
        words.length,
        'words'
      );

      // Create word cloud layout
      const layout = cloud()
        .size([width, height])
        .words(words.map(d => ({ ...d, text: d.text })))
        .padding(4)
        .rotate(() => 0)
        .font('Inter, system-ui, sans-serif')
        .fontSize(d => d.size)
        .spiral('archimedean')
        .random(() => 0.5)
        .on('end', draw);

      layout.start();

      function draw(cloudWords) {
        if (cloudWords.length === 0) {
          console.log('[WordCloud] Layout complete but no words positioned');
          // Clear if no words
          svg
            .selectAll('g.word-cloud-group')
            .selectAll('text')
            .transition()
            .duration(300)
            .style('opacity', 0)
            .remove();
          return;
        }

        console.log(
          '[WordCloud] Layout complete, drawing',
          cloudWords.length,
          'words'
        );

        // Ensure group exists
        let g = svg.select('g.word-cloud-group');
        if (g.empty()) {
          g = svg
            .append('g')
            .attr('class', 'word-cloud-group')
            .attr('transform', `translate(${width / 2},${height / 2})`);
        }

        // Data join with key function for smooth transitions
        const textElements = g.selectAll('text').data(cloudWords, d => d.text);

        // EXIT: Remove words that are no longer in the data
        textElements
          .exit()
          .transition()
          .duration(300)
          .style('font-size', 0)
          .style('opacity', 0)
          .remove();

        // UPDATE: Transition existing words to new positions/sizes/colors
        textElements
          .transition()
          .duration(600)
          .ease(d3.easeCubicInOut)
          .attr('transform', d => `translate(${d.x},${d.y})`)
          .style('font-size', d => `${d.size}px`)
          .style('fill', d => getSentimentColor(d.sentiment))
          .style('opacity', 1);

        // ENTER: Add new words
        textElements
          .enter()
          .append('text')
          .style('font-family', 'Inter, system-ui, sans-serif')
          .style('cursor', 'pointer')
          .attr('text-anchor', 'middle')
          .text(d => d.text)
          .style('font-size', d => `${d.size}px`)
          .style('font-weight', '500')
          .style('fill', d => getSentimentColor(d.sentiment))
          .attr('transform', d => `translate(${d.x},${d.y})`)
          .style('opacity', 0)
          .on('click', function (event, d) {
            setSelectedKeyword(d);
            setSidebarOpen(true);
            hideTooltip();
          })
          .on('mouseover', function (event, d) {
            d3.select(this)
              .transition()
              .duration(150)
              .style('font-size', `${d.size * 1.15}px`)
              .style('opacity', 0.7);
            showTooltip(event, d);
          })
          .on('mouseout', function (event, d) {
            d3.select(this)
              .transition()
              .duration(150)
              .style('font-size', `${d.size}px`)
              .style('opacity', 1);
            hideTooltip();
          })
          .transition()
          .duration(600)
          .delay((d, i) => i * 40)
          .style('opacity', 1);

        console.log('[WordCloud] Draw complete');
      }
    };

    renderWordCloud(words);
  }, [
    data,
    currentDayIndex,
    selectedDate,
    getSentimentColor,
    showTooltip,
    hideTooltip,
    getKeywordsForCurrentDate,
  ]);

  if (loading) {
    return (
      <div className="word-cloud-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading intelligence data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="word-cloud-container">
        <div className="error-state">
          <p>Error loading data: {error}</p>
          <p className="error-hint">
            Make sure the API server is running at {API_BASE_URL}
          </p>
        </div>
      </div>
    );
  }

  const handleTeamChange = e => {
    const value = e.target.value;
    if (value === '') {
      setSelectedTeam(null);
      setData(null);
    } else {
      setSelectedTeam(value);
    }
    setCurrentDayIndex(dateRange.length - 1); // Start at most recent date
    setIsPlaying(false);
    setSidebarOpen(false);
  };

  const handleSliderChange = e => {
    setCurrentDayIndex(parseInt(e.target.value));
    setIsPlaying(false);
    setSidebarOpen(false);
  };

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="word-cloud-container">
      <div className="word-cloud-header">
        <div className="team-selector-container">
          <select
            className="team-selector"
            value={selectedTeam || ''}
            onChange={handleTeamChange}
            aria-label="Select team"
          >
            <option value="">Choose a team</option>
            {teams.map(team => (
              <option key={team.key} value={team.key}>
                {team.name}
              </option>
            ))}
          </select>
          <span className="selector-subtitle">Daily Trend Digest</span>
        </div>
      </div>

      {!selectedTeam && (
        <div className="word-cloud-content">
          <div className="word-cloud-card">
            <div className="empty-state">
              <p>Please select a team to view the word cloud</p>
            </div>
          </div>
        </div>
      )}

      {selectedTeam && !data && (
        <div className="word-cloud-content">
          <div className="word-cloud-card">
            <div className="empty-state">
              <p>No data available</p>
            </div>
          </div>
        </div>
      )}

      {selectedTeam && data && data.keywords && data.keywords.length > 0 && (
        <div className="word-cloud-content">
          <div className="word-cloud-card">
            <div className="word-cloud-visualization">
              <svg ref={svgRef} className="word-cloud-svg"></svg>
            </div>

            <div className="sentiment-legend">
              <h4>Sentiment Legend</h4>
              <div className="legend-items">
                <div className="legend-item">
                  <span className="legend-color positive"></span>
                  <span>Positive</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color neutral"></span>
                  <span>Neutral</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color negative"></span>
                  <span>Negative</span>
                </div>
              </div>
              <p className="legend-note">
                Color intensity indicates sentiment magnitude
              </p>
            </div>

            <div className="word-cloud-controls">
              <button
                className="play-button"
                onClick={togglePlay}
                aria-label={isPlaying ? 'Pause' : 'Play'}
                disabled={dateRange.length <= 1}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>

              <div className="slider-container">
                <input
                  type="range"
                  min="0"
                  max={dateRange.length - 1}
                  value={currentDayIndex}
                  onChange={handleSliderChange}
                  className="time-slider"
                  title={selectedDate}
                  disabled={dateRange.length <= 1}
                />
                <div className="slider-labels">
                  <span className="current-date">{selectedDate}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar for document list */}
          <div className={`keyword-sidebar ${sidebarOpen ? 'open' : ''}`}>
            <div className="sidebar-header">
              <h3>{selectedKeyword?.text}</h3>
              <button
                className="sidebar-close"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close sidebar"
              >
                ×
              </button>
            </div>
            {selectedKeyword && (
              <div className="sidebar-content">
                <div className="keyword-stats">
                  <div className="stat-item">
                    <span className="stat-label">Importance:</span>
                    <span className="stat-value">
                      {selectedKeyword.importance.toFixed(2)}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Documents:</span>
                    <span className="stat-value">
                      {selectedKeyword.documents?.length || 0}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Velocity:</span>
                    <span className="stat-value">
                      {selectedKeyword.metrics.velocity.toFixed(2)}%
                    </span>
                  </div>
                </div>

                <ImportanceTrendChart
                  keyword={selectedKeyword.text}
                  timeSeries={getImportanceTimeSeries(selectedKeyword)}
                />

                <div className="documents-section">
                  <h4>Related Documents</h4>
                  <div className="documents-list">
                    {selectedKeyword.documents?.map((doc, idx) => (
                      <div key={idx} className="document-item">
                        <h5 className="document-title">
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {doc.title}
                          </a>
                        </h5>
                        <div className="document-meta">
                          <span className="document-source">
                            {doc.source_name}
                          </span>
                          <span className="document-date">
                            {new Date(doc.published_date).toLocaleDateString(
                              'en-US',
                              {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              }
                            )}
                          </span>
                        </div>
                        <p className="document-snippet">{doc.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tooltip */}
      <div id="word-cloud-tooltip" className="word-cloud-tooltip"></div>
    </div>
  );
}

export default WordCloudTimeline;
