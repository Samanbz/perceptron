import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const { user, logout } = useAuth();

  // Get first name from full name
  const firstName = user?.name?.split(' ')[0] || 'User';
  
  // Get initials for avatar
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Mock data for demonstration
  const stats = [
    { label: 'Active Teams', value: '4', change: '+12%', icon: '👥' },
    { label: 'Data Sources', value: '12', change: '+3', icon: '📊' },
    { label: 'Insights Today', value: '847', change: '+24%', icon: '💡' },
    { label: 'Processing Speed', value: '2.3s', change: '-15%', icon: '⚡' }
  ];

  const recentInsights = [
    {
      team: 'Market Intelligence',
      title: 'Emerging trend in renewable energy sector',
      time: '5 minutes ago',
      priority: 'high'
    },
    {
      team: 'Competitor Analysis',
      title: 'New product launch detected: Tech Corp',
      time: '12 minutes ago',
      priority: 'medium'
    },
    {
      team: 'Risk Assessment',
      title: 'Regulatory changes in EU market',
      time: '28 minutes ago',
      priority: 'high'
    },
    {
      team: 'Consumer Sentiment',
      title: 'Positive sentiment shift in Q4 campaigns',
      time: '1 hour ago',
      priority: 'low'
    }
  ];

  const activeTeams = [
    {
      name: 'Market Intelligence',
      status: 'active',
      sources: 8,
      lastUpdate: '2 min ago',
      color: '#0018A8'
    },
    {
      name: 'Competitor Analysis',
      status: 'active',
      sources: 5,
      lastUpdate: '5 min ago',
      color: '#00A3E0'
    },
    {
      name: 'Risk Assessment',
      status: 'processing',
      sources: 12,
      lastUpdate: '10 min ago',
      color: '#08197B'
    },
    {
      name: 'Consumer Sentiment',
      status: 'active',
      sources: 6,
      lastUpdate: '15 min ago',
      color: '#00D4FF'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-sidebar">
        <div className="sidebar-header">
          <Link to="/" className="sidebar-logo">
            <img src="/logo_solo.png" alt="Perceptron" className="sidebar-logo-image" />
            <span>Perceptron</span>
          </Link>
        </div>

        <nav className="sidebar-nav">
          <button 
            className={`sidebar-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <span className="nav-icon">📊</span>
            <span>Overview</span>
          </button>
          <button 
            className={`sidebar-nav-item ${activeTab === 'teams' ? 'active' : ''}`}
            onClick={() => setActiveTab('teams')}
          >
            <span className="nav-icon">👥</span>
            <span>Intelligence Teams</span>
          </button>
          <button 
            className={`sidebar-nav-item ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <span className="nav-icon">💡</span>
            <span>Insights</span>
          </button>
          <button 
            className={`sidebar-nav-item ${activeTab === 'sources' ? 'active' : ''}`}
            onClick={() => setActiveTab('sources')}
          >
            <span className="nav-icon">🔗</span>
            <span>Data Sources</span>
          </button>
          <button 
            className={`sidebar-nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <span className="nav-icon">📈</span>
            <span>Analytics</span>
          </button>
          <button 
            className={`sidebar-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">{getInitials(user?.name)}</div>
            <div className="user-info">
              <div className="user-name">{user?.name || 'User'}</div>
              <div className="user-email">{user?.email || ''}</div>
            </div>
          </div>
          <button onClick={logout} className="sidebar-logout">
            <span className="nav-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="dashboard-header">
          <div className="dashboard-header-content">
            <h1>Welcome back, {firstName}</h1>
            <p>Here&apos;s what&apos;s happening with your intelligence teams today</p>
          </div>
          <div className="dashboard-header-actions">
            <button className="btn-secondary-small">
              <span>📥</span> Export Report
            </button>
            <button className="btn-primary-small">
              <span>➕</span> New Team
            </button>
          </div>
        </div>

        <div className="dashboard-content">
          {/* Stats Grid */}
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div key={index} className="stat-card">
                <div className="stat-icon">{stat.icon}</div>
                <div className="stat-content">
                  <div className="stat-label">{stat.label}</div>
                  <div className="stat-value">{stat.value}</div>
                  <div className={`stat-change ${stat.change.startsWith('+') ? 'positive' : 'negative'}`}>
                    {stat.change} from last week
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="dashboard-grid">
            {/* Recent Insights */}
            <div className="dashboard-card">
              <div className="card-header">
                <h2>Recent Insights</h2>
                <button className="btn-text">View All</button>
              </div>
              <div className="insights-list">
                {recentInsights.map((insight, index) => (
                  <div key={index} className="insight-item">
                    <div className={`insight-priority ${insight.priority}`}></div>
                    <div className="insight-content">
                      <div className="insight-team">{insight.team}</div>
                      <div className="insight-title">{insight.title}</div>
                      <div className="insight-time">{insight.time}</div>
                    </div>
                    <button className="insight-action">→</button>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Teams */}
            <div className="dashboard-card">
              <div className="card-header">
                <h2>Active Teams</h2>
                <button className="btn-text">Manage</button>
              </div>
              <div className="teams-list">
                {activeTeams.map((team, index) => (
                  <div key={index} className="team-item">
                    <div className="team-color" style={{ backgroundColor: team.color }}></div>
                    <div className="team-content">
                      <div className="team-name">{team.name}</div>
                      <div className="team-meta">
                        <span className={`team-status ${team.status}`}>
                          {team.status === 'active' ? '● Active' : '⟳ Processing'}
                        </span>
                        <span className="team-sources">{team.sources} sources</span>
                      </div>
                    </div>
                    <div className="team-update">{team.lastUpdate}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Activity Chart Placeholder */}
          <div className="dashboard-card">
            <div className="card-header">
              <h2>Activity Overview</h2>
              <div className="chart-filters">
                <button className="filter-btn active">7D</button>
                <button className="filter-btn">30D</button>
                <button className="filter-btn">90D</button>
              </div>
            </div>
            <div className="chart-placeholder">
              <div className="chart-visual">
                <div className="chart-bar" style={{ height: '60%' }}></div>
                <div className="chart-bar" style={{ height: '80%' }}></div>
                <div className="chart-bar" style={{ height: '45%' }}></div>
                <div className="chart-bar" style={{ height: '90%' }}></div>
                <div className="chart-bar" style={{ height: '70%' }}></div>
                <div className="chart-bar" style={{ height: '85%' }}></div>
                <div className="chart-bar" style={{ height: '95%' }}></div>
              </div>
              <div className="chart-labels">
                <span>Mon</span>
                <span>Tue</span>
                <span>Wed</span>
                <span>Thu</span>
                <span>Fri</span>
                <span>Sat</span>
                <span>Sun</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
