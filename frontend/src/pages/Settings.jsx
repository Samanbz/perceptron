import React, { useState, useEffect } from 'react';
import './Settings.css';

function Settings() {
    const [extensionInstalled, setExtensionInstalled] = useState(false);
    const [scoutingEnabled, setScoutingEnabled] = useState(false);
    const [stats, setStats] = useState({
        pagesScanned: 0,
        todayScans: 0,
        relevantPages: 0
    });

    useEffect(() => {
        checkExtensionStatus();
        loadStats();
    }, []);

    const checkExtensionStatus = () => {
        // Check if extension is installed by looking for a specific element or message
        window.postMessage({ type: 'CHECK_EXTENSION' }, '*');

        // Listen for response
        const handleMessage = (event) => {
            if (event.data.type === 'EXTENSION_INSTALLED') {
                setExtensionInstalled(true);
                setScoutingEnabled(event.data.scoutingEnabled);
            }
        };

        window.addEventListener('message', handleMessage);

        // Timeout check
        setTimeout(() => {
            window.removeEventListener('message', handleMessage);
        }, 1000);
    };

    const loadStats = async() => {
        try {
            const response = await fetch('http://localhost:8000/api/scout/stats');
            if (response.ok) {
                const data = await response.json();
                setStats({
                    pagesScanned: data.total_pages_scouted || 0,
                    todayScans: data.pages_today || 0,
                    relevantPages: data.relevant_pages || 0
                });
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const toggleScouting = () => {
        const newState = !scoutingEnabled;
        setScoutingEnabled(newState);

        // Send message to extension
        window.postMessage({
            type: 'TOGGLE_SCOUTING',
            enabled: newState
        }, '*');

        // Also store in localStorage as backup
        localStorage.setItem('scoutingEnabled', newState);
    };

    const downloadExtension = () => {
        // Create a zip file or provide instructions
        alert('Extension download will be available soon! For now, follow the manual installation guide.');
    };

    return (
        <div className="page settings-page">
            <div className="container">
                <div className="settings-header">
                    <h1>⚙️ Settings & Scouting Control</h1>
                    <p>Manage your Perceptron Scout extension and preferences</p>
                </div>

                {/* Extension Status Card */}
                <div className="settings-section">
                    <div className={`status-card ${extensionInstalled ? 'installed' : 'not-installed'}`}>
                        <div className="status-icon">{extensionInstalled ? '✅' : '📦'}</div>
                        <div className="status-info">
                            <h2>Browser Extension</h2>
                            <p className="status-label">{extensionInstalled ? 'Installed & Active' : 'Not Installed'}</p>
                        </div>
                        {!extensionInstalled && (
                            <button className="btn-primary" onClick={downloadExtension}>
                                Install Extension
                            </button>
                        )}
                    </div>
                </div>

                {/* Scouting Control */}
                {extensionInstalled && (
                    <div className="settings-section">
                        <div className="control-card">
                            <div className="control-header">
                                <div>
                                    <h3>🎯 Scouting Mode</h3>
                                    <p className="control-description">
                                        Automatically analyze and categorize web pages as you browse
                                    </p>
                                </div>
                                <label className="toggle-switch-large">
                                    <input
                                        type="checkbox"
                                        checked={scoutingEnabled}
                                        onChange={toggleScouting}
                                    />
                                    <span className="slider-large"></span>
                                </label>
                            </div>

                            <div className="control-status">
                                <div className={`status-indicator ${scoutingEnabled ? 'active' : 'inactive'}`}>
                                    <span className="status-dot"></span>
                                    <span className="status-text">
                                        {scoutingEnabled ? 'Active - Analyzing pages' : 'Paused - Not analyzing'}
                                    </span>
                                </div>
                            </div>

                            {scoutingEnabled && (
                                <div className="control-info">
                                    <div className="info-item">
                                        <span className="info-icon">🔍</span>
                                        <span>Pages are automatically scanned when you visit them</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-icon">🎨</span>
                                        <span>Relevant content gets categorized by team</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-icon">🔔</span>
                                        <span>Notifications appear for high-relevance matches</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Stats Dashboard */}
                {extensionInstalled && (
                    <div className="settings-section">
                        <h3>📊 Scouting Statistics</h3>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-value">{stats.pagesScanned}</div>
                                <div className="stat-label">Total Pages Scanned</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{stats.todayScans}</div>
                                <div className="stat-label">Scanned Today</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{stats.relevantPages}</div>
                                <div className="stat-label">Relevant Matches</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Installation Guide */}
                {!extensionInstalled && (
                    <div className="settings-section">
                        <div className="installation-guide">
                            <h3>🚀 Quick Installation Guide</h3>
                            <div className="guide-steps">
                                <div className="guide-step">
                                    <div className="step-number">1</div>
                                    <div className="step-content">
                                        <h4>Download Extension Files</h4>
                                        <p>Click the button above to download the extension package</p>
                                    </div>
                                </div>
                                <div className="guide-step">
                                    <div className="step-number">2</div>
                                    <div className="step-content">
                                        <h4>Open Chrome Extensions</h4>
                                        <p>Go to <code>chrome://extensions/</code> in your browser</p>
                                    </div>
                                </div>
                                <div className="guide-step">
                                    <div className="step-number">3</div>
                                    <div className="step-content">
                                        <h4>Enable Developer Mode</h4>
                                        <p>Toggle &quot;Developer mode&quot; in the top right corner</p>
                                    </div>
                                </div>
                                <div className="guide-step">
                                    <div className="step-number">4</div>
                                    <div className="step-content">
                                        <h4>Load Extension</h4>
                                        <p>Click &quot;Load unpacked&quot; and select the extension folder</p>
                                    </div>
                                </div>
                                <div className="guide-step">
                                    <div className="step-number">5</div>
                                    <div className="step-content">
                                        <h4>Start Scouting!</h4>
                                        <p>Refresh this page and enable scouting mode</p>
                                    </div>
                                </div>
                            </div>

                            <div className="alternative-method">
                                <h4>💡 Alternative: One-Click Install (Coming Soon)</h4>
                                <p>
                                    We&apos;re working on publishing to the Chrome Web Store for easier installation. Stay tuned for updates!
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Advanced Settings */}
                <div className="settings-section">
                    <h3>⚙️ Advanced Settings</h3>
                    <div className="settings-list">
                        <div className="setting-item">
                            <div className="setting-info">
                                <h4>Notification Threshold</h4>
                                <p>Minimum relevance score to show notifications</p>
                            </div>
                            <select className="setting-input">
                                <option value="0.3">30% (Show more)</option>
                                <option value="0.5" selected>50% (Balanced)</option>
                                <option value="0.7">70% (Show less)</option>
                            </select>
                        </div>

                        <div className="setting-item">
                            <div className="setting-info">
                                <h4>Notification Duration</h4>
                                <p>How long notifications stay on screen</p>
                            </div>
                            <select className="setting-input">
                                <option value="3">3 seconds</option>
                                <option value="5" selected>5 seconds</option>
                                <option value="10">10 seconds</option>
                            </select>
                        </div>

                        <div className="setting-item">
                            <div className="setting-info">
                                <h4>Cache Duration</h4>
                                <p>How long to remember analyzed pages</p>
                            </div>
                            <select className="setting-input">
                                <option value="30">30 minutes</option>
                                <option value="60" selected>1 hour</option>
                                <option value="180">3 hours</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="settings-section">
                    <h3>🔧 Quick Actions</h3>
                    <div className="actions-grid">
                        <button className="action-button">
                            <span className="action-icon">🔄</span>
                            <span className="action-label">Refresh Stats</span>
                        </button>
                        <button className="action-button">
                            <span className="action-icon">🗑️</span>
                            <span className="action-label">Clear Cache</span>
                        </button>
                        <button className="action-button">
                            <span className="action-icon">📥</span>
                            <span className="action-label">Export Data</span>
                        </button>
                        <button className="action-button">
                            <span className="action-icon">📖</span>
                            <span className="action-label">View Guide</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Settings;