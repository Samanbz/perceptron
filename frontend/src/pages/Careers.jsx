import React, { useState } from 'react';

function Careers() {
    const [selectedDepartment, setSelectedDepartment] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedLocation, setSelectedLocation] = useState('all');
    const [selectedType, setSelectedType] = useState('all');

    const departments = [
        { id: 'all', name: 'All Teams', icon: '🏢' },
        { id: 'engineering', name: 'Engineering', icon: '💻' },
        { id: 'design', name: 'Design', icon: '🎨' },
        { id: 'product', name: 'Product', icon: '📊' },
        { id: 'sales', name: 'Sales & Marketing', icon: '📢' },
        { id: 'operations', name: 'Operations', icon: '⚙️' }
    ];

    const locations = [
        { id: 'all', name: 'All Locations' },
        { id: 'remote', name: 'Remote' },
        { id: 'us', name: 'United States' },
        { id: 'europe', name: 'Europe' },
        { id: 'asia', name: 'Asia' }
    ];

    const jobTypes = [
        { id: 'all', name: 'All Types' },
        { id: 'full-time', name: 'Full-time' },
        { id: 'part-time', name: 'Part-time' },
        { id: 'contract', name: 'Contract' },
        { id: 'internship', name: 'Internship' }
    ];

    const benefits = [{
            icon: '🏥',
            title: 'Health & Wellness',
            description: 'Comprehensive medical, dental, and vision coverage for you and your family'
        },
        {
            icon: '💰',
            title: 'Competitive Salary',
            description: 'Industry-leading compensation and equity packages'
        },
        {
            icon: '🌴',
            title: 'Unlimited PTO',
            description: 'Take time off when you need it to recharge and stay balanced'
        },
        {
            icon: '🏠',
            title: 'Remote Work',
            description: 'Work from anywhere with flexible hours that fit your lifestyle'
        },
        {
            icon: '📚',
            title: 'Learning Budget',
            description: 'Annual budget for courses, conferences, and professional development'
        },
        {
            icon: '🎯',
            title: 'Career Growth',
            description: 'Clear career paths with mentorship and advancement opportunities'
        }
    ];

    return (
        <div className="careers-page">
            {/* Hero Section */}
            <section className="careers-hero">
                <div className="careers-hero-content">
                    <h1 className="careers-hero-title">Careers at Perceptron</h1>
                    <p className="careers-hero-subtitle">
                        Join us in building the future of intelligence platforms
                    </p>
                    <p className="careers-hero-description">
                        We&apos;re a team of passionate builders, thinkers, and innovators working to transform how organizations gather and analyze intelligence. If you&apos;re excited about solving complex problems and making an impact, we&apos;d love to hear from you.
                    </p>
                </div>
            </section>

            {/* Stats Section */}
            <section className="careers-stats">
                <div className="careers-stats-content">
                    <div className="stat-item">
                        <div className="stat-number">50+</div>
                        <div className="stat-label">Team Members</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-number">15+</div>
                        <div className="stat-label">Countries</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-number">100%</div>
                        <div className="stat-label">Remote</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-number">4.8★</div>
                        <div className="stat-label">Glassdoor Rating</div>
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="careers-section">
                <div className="careers-section-content">
                    <h2 className="careers-section-title">Benefits & Perks</h2>
                    <p className="careers-section-subtitle">
                        We believe in taking care of our team so they can do their best work
                    </p>
                    <div className="benefits-grid">
                        {benefits.map((benefit, index) => (
                            <div key={index} className="benefit-card">
                                <div className="benefit-icon">{benefit.icon}</div>
                                <h3 className="benefit-title">{benefit.title}</h3>
                                <p className="benefit-description">{benefit.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Open Positions Section */}
            <section className="careers-section careers-positions-section">
                <div className="careers-section-content">
                    <h2 className="careers-section-title">Open Positions</h2>
                    <p className="careers-section-subtitle">
                        Explore opportunities across our teams
                    </p>

                    {/* Search and Filter Bar */}
                    <div className="job-search-container">
                        <div className="search-bar">
                            <svg className="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                            </svg>
                            <input
                                type="text"
                                className="search-input"
                                placeholder="Search by job title, keyword, or team..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        <div className="filter-controls">
                            <select
                                className="filter-select"
                                value={selectedDepartment}
                                onChange={(e) => setSelectedDepartment(e.target.value)}
                            >
                                {departments.map(dept => (
                                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                                ))}
                            </select>

                            <select
                                className="filter-select"
                                value={selectedLocation}
                                onChange={(e) => setSelectedLocation(e.target.value)}
                            >
                                {locations.map(loc => (
                                    <option key={loc.id} value={loc.id}>{loc.name}</option>
                                ))}
                            </select>

                            <select
                                className="filter-select"
                                value={selectedType}
                                onChange={(e) => setSelectedType(e.target.value)}
                            >
                                {jobTypes.map(type => (
                                    <option key={type.id} value={type.id}>{type.name}</option>
                                ))}
                            </select>

                            <button
                                className="clear-filters-btn"
                                onClick={() => {
                                    setSearchQuery('');
                                    setSelectedDepartment('all');
                                    setSelectedLocation('all');
                                    setSelectedType('all');
                                }}
                            >
                                Clear Filters
                            </button>
                        </div>
                    </div>

                    {/* No Positions Message */}
                    <div className="no-positions-container">
                        <div className="no-positions-icon">💼</div>
                        <h3 className="no-positions-title">No Open Positions</h3>
                        <p className="no-positions-text">
                            We don&apos;t have any open positions at the moment, but we&apos;re always looking for talented people to join our team. Submit your resume and we&apos;ll reach out when a role that matches your skills becomes available.
                        </p>
                        <a href="mailto:careers@perceptron.ai" className="btn-primary">
                            Submit Your Resume
                        </a>
                    </div>
                </div>
            </section>

            {/* Life at Perceptron Section */}
            <section className="careers-section careers-culture-section">
                <div className="careers-section-content">
                    <h2 className="careers-section-title">Life at Perceptron</h2>
                    <p className="careers-section-subtitle">
                        Our culture and values
                    </p>
                    <div className="culture-grid">
                        <div className="culture-card">
                            <h3>🚀 Move Fast</h3>
                            <p>We ship quickly and iterate based on feedback. Speed is a competitive advantage.</p>
                        </div>
                        <div className="culture-card">
                            <h3>🎯 Focus on Impact</h3>
                            <p>We prioritize work that creates the most value for our customers and team.</p>
                        </div>
                        <div className="culture-card">
                            <h3>🤝 Default to Transparency</h3>
                            <p>We share information openly and communicate clearly across all levels.</p>
                        </div>
                        <div className="culture-card">
                            <h3>💡 Stay Curious</h3>
                            <p>We ask questions, challenge assumptions, and continuously learn and grow.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="careers-cta">
                <div className="careers-cta-content">
                    <h2 className="careers-cta-title">Ready to Make an Impact?</h2>
                    <p className="careers-cta-text">
                        Join our team and help build the future of intelligence platforms
                    </p>
                    <a href="mailto:careers@perceptron.ai" className="btn-primary btn-large">
                        Get in Touch
                    </a>
                </div>
            </section>
        </div>
    );
}

export default Careers;