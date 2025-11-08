import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
import './WordCloudTimeline.css';

// Available teams configuration
const TEAMS = [{
        key: 'regulator',
        name: 'Regulatory Team',
        file: 'mock_data_regulator_wordcloud.json',
    },
    {
        key: 'competitor',
        name: 'Competitive Intelligence',
        file: 'mock_data_competitor_wordcloud.json',
    },
    {
        key: 'investor',
        name: 'Investment Team',
        file: 'mock_data_investor_wordcloud.json',
    },
    {
        key: 'researcher',
        name: 'Research Team',
        file: 'mock_data_researcher_wordcloud.json',
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
    const [currentDayIndex, setCurrentDayIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [selectedKeyword, setSelectedKeyword] = useState(null);
    const [selectedTeam, setSelectedTeam] = useState(TEAMS[0].key); // Auto-select first team
    const svgRef = useRef(null);
    const playIntervalRef = useRef(null);

    // Load mock data when component mounts or team changes
    useEffect(() => {
        const teamConfig = TEAMS.find(t => t.key === selectedTeam);
        if (!teamConfig) return;

        setLoading(true);
        setError(null);
        fetch(`/${teamConfig.file}`)
            .then(response => {
                if (!response.ok)
                    throw new Error(
                        `Failed to load data: ${response.status} ${response.statusText}`
                    );
                return response.json();
            })
            .then(jsonData => {
                setData(jsonData);
                setLoading(false);
            })
            .catch(err => {
                console.error('WordCloudTimeline: Error loading data:', err);
                setError(err.message);
                setLoading(false);
            });
    }, [selectedTeam]);

    // Auto-play functionality
    useEffect(() => {
        if (isPlaying && data) {
            const uniqueDatesCount = [...new Set(data.keywords.map(kw => kw.date))].length;
            playIntervalRef.current = setInterval(() => {
                setCurrentDayIndex(prev => {
                    if (prev >= uniqueDatesCount - 1) {
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
    }, [isPlaying, data]);

    /**
     * Group keywords by date to get unique dates
     */
    const getUniqueDates = useCallback(() => {
        if (!data || !data.keywords) return [];
        const dates = [...new Set(data.keywords.map(kw => kw.date))].sort();
        return dates;
    }, [data]);

    /**
     * Get keywords for a specific date
     */
    const getKeywordsForDate = useCallback((dateIndex) => {
        if (!data || !data.keywords) return [];
        const uniqueDates = getUniqueDates();
        if (dateIndex >= uniqueDates.length) return [];
        const targetDate = uniqueDates[dateIndex];
        return data.keywords.filter(kw => kw.date === targetDate);
    }, [data, getUniqueDates]);

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
            d.sentiment.score > 0.2 ?
            'Positive' :
            d.sentiment.score < -0.2 ?
            'Negative' :
            'Neutral';

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
    const getImportanceTimeSeries = useCallback((keywordData) => {
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
    }, [data]);

    // Render word cloud when data or day changes
    useEffect(() => {
        if (!data || !svgRef.current) return;

        const keywords = data.keywords;
        if (!keywords || keywords.length === 0) return;

        // Get keywords for the current date
        const currentDateKeywords = getKeywordsForDate(currentDayIndex);
        if (currentDateKeywords.length === 0) return;

        // Prepare words for cloud layout - use ALL keywords from this date
        const words = currentDateKeywords.map((kw, idx) => ({
            text: kw.keyword,
            // First keyword gets larger size, others scaled by importance
            size: idx === 0 ?
                Math.max(16, Math.min(48, kw.importance * 0.5)) :
                Math.max(10, Math.min(32, kw.importance * 0.35)),
            importance: kw.importance,
            sentiment: kw.sentiment,
            metrics: kw.metrics,
            documents: kw.documents,
        }));

        /**
         * Renders the word cloud using D3 cloud layout
         */
        const renderWordCloud = words => {
            const svg = d3.select(svgRef.current);
            const width = svgRef.current.clientWidth;
            const height = svgRef.current.clientHeight;

            if (width === 0 || height === 0) {
                return;
            }

            // Create word cloud layout
            const layout = cloud()
                .size([width, height])
                .words(words.map(d => ({...d, text: d.text })))
                .padding(3)
                .rotate(() => 0)
                .font('Inter, system-ui, sans-serif')
                .fontSize(d => d.size)
                .spiral('archimedean')
                .random(() => 0.5)
                .on('end', draw);

            layout.start();

            function draw(cloudWords) {
                if (cloudWords.length === 0) return;

                // Ensure group exists (don't clear on every render)
                let g = svg.select('g.word-cloud-group');
                if (g.empty()) {
                    g = svg
                        .append('g')
                        .attr('class', 'word-cloud-group')
                        .attr('transform', `translate(${width / 2},${height / 2})`);
                }

                // Data join with key function for object constancy
                const textElements = g.selectAll('text').data(cloudWords, d => d.text);

                // Enter: new words
                const enterWords = textElements
                    .enter()
                    .append('text')
                    .style('font-family', 'Inter, system-ui, sans-serif')
                    .style('cursor', 'pointer')
                    .attr('text-anchor', 'middle')
                    .text(d => d.text)
                    .style('font-size', d => `${d.size}px`)
                    .style('font-weight', '500')
                    .style('fill', d => getSentimentColor(d.sentiment))
                    .style('opacity', 0)
                    .attr('transform', d => `translate(${d.x},${d.y})`)
                    .on('click', function(event, d) {
                        setSelectedKeyword(d);
                        setSidebarOpen(true);
                        hideTooltip();
                    })
                    .on('mouseover', function(event, d) {
                        d3.select(this)
                            .transition()
                            .duration(200)
                            .style('font-size', `${d.size * 1.15}px`)
                            .style('opacity', 0.7);
                        showTooltip(event, d);
                    })
                    .on('mouseout', function(event, d) {
                        d3.select(this)
                            .transition()
                            .duration(200)
                            .style('font-size', `${d.size}px`)
                            .style('opacity', 1);
                        hideTooltip();
                    });

                // Animate enter
                enterWords
                    .transition()
                    .duration(600)
                    .delay((d, i) => i * 50)
                    .style('opacity', 1);

                // Update: existing words - smooth transition to new position/size/color
                textElements
                    .transition()
                    .duration(800)
                    .ease(d3.easeCubicInOut)
                    .attr('transform', d => `translate(${d.x},${d.y})`)
                    .style('font-size', d => `${d.size}px`)
                    .style('font-weight', '500')
                    .style('fill', d => getSentimentColor(d.sentiment))
                    .style('opacity', 1);

                // Exit: removed words
                textElements
                    .exit()
                    .transition()
                    .duration(400)
                    .style('font-size', 0)
                    .style('opacity', 0)
                    .remove();
            }
        };

        renderWordCloud(words);
    }, [data, currentDayIndex, getSentimentColor, showTooltip, hideTooltip, getKeywordsForDate]);

    const handleSliderChange = e => {
        setCurrentDayIndex(parseInt(e.target.value));
        setIsPlaying(false);
    };

    const togglePlay = () => {
        setIsPlaying(!isPlaying);
    };

    const handleExportReport = async (keyword) => {
        try {
            // Show loading state or disable button
            const exportButton = document.querySelector('.export-button');
            if (exportButton) {
                exportButton.disabled = true;
                exportButton.textContent = 'Generating...';
            }

            // Prepare data for the report
            const reportData = {
                keyword: keyword.text,
                importance: keyword.importance,
                metrics: keyword.metrics,
                documents: keyword.documents,
                timeSeries: getImportanceTimeSeries(keyword),
                team: selectedTeam,
                currentDate: currentDate
            };

            // Make API call to generate PDF report
            const response = await fetch('/api/generate-keyword-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reportData)
            });

            if (!response.ok) {
                throw new Error(`Failed to generate report: ${response.statusText}`);
            }

            // Get the PDF blob
            const blob = await response.blob();

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${keyword.text}-report-${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Error generating report:', error);
            alert('Failed to generate report. Please try again.');
        } finally {
            // Reset button state
            const exportButton = document.querySelector('.export-button');
            if (exportButton) {
                exportButton.disabled = false;
                exportButton.textContent = '📄 Export Report';
            }
        }
    };

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
        setCurrentDayIndex(0);
        setIsPlaying(false);
        setSidebarOpen(false);
    };

    const uniqueDates = data ? getUniqueDates() : [];
    const currentDate = uniqueDates[currentDayIndex];

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
                        {TEAMS.map(team => (
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
            )}        {
            selectedTeam && data && data.keywords && data.keywords.length > 0 && (
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
                                disabled={uniqueDates.length <= 1}
                            >
                                {isPlaying ? '⏸' : '▶'}
                            </button>

                            <div className="slider-container">
                                <input
                                    type="range"
                                    min="0"
                                    max={uniqueDates.length - 1}
                                    value={currentDayIndex}
                                    onChange={handleSliderChange}
                                    className="time-slider"
                                    title={currentDate}
                                    disabled={uniqueDates.length <= 1}
                                />
                                <div className="slider-labels">
                                    <span className="current-date">{currentDate}</span>
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
                                        <span className="stat-value">{selectedKeyword.importance.toFixed(2)}</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-label">Documents:</span>
                                        <span className="stat-value">{selectedKeyword.documents?.length || 0}</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-label">Velocity:</span>
                                        <span className="stat-value">{selectedKeyword.metrics.velocity.toFixed(2)}%</span>
                                    </div>
                                </div>

                                <div className="sidebar-actions">
                                    <button
                                        className="export-button"
                                        onClick={() => handleExportReport(selectedKeyword)}
                                        aria-label="Export PDF Report"
                                    >
                                        📄 Export Report
                                    </button>
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
                                                    <span className="document-source">{doc.source_name}</span>
                                                    <span className="document-date">
                                                        {new Date(doc.published_date).toLocaleDateString('en-US', {
                                                            year: 'numeric',
                                                            month: 'short',
                                                            day: 'numeric',
                                                        })}
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