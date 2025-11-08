import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Header() {
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
  };

  const getUserInitials = () => {
    if (!user) return '';
    return user.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <nav className={`nav ${scrolled ? 'scrolled' : ''}`}>
      <div className="nav-content">
        {/* Logo Section */}
        <Link to="/" className="nav-logo">
          <img src="/Capture d'écran 2025-11-07 225701.png" alt="Perceptron Logo" className="logo-image" />
        </Link>

        {/* Navigation Links */}
        <div className="nav-menu">
          <Link 
            to="/dashboard" 
            className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link 
            to="/peers-newsroom" 
            className={`nav-link ${location.pathname === '/peers-newsroom' ? 'active' : ''}`}
          >
            Peers Newsroom
          </Link>
          <Link 
            to="/reputation-map" 
            className={`nav-link ${location.pathname === '/reputation-map' ? 'active' : ''}`}
          >
            Reputation Map
          </Link>
        </div>

        {/* User Menu - Profile and Sign Out */}
        <div className="nav-auth">
          {/* Profile Picture */}
          <Link 
            to="/profile" 
            className="user-avatar"
            title="Profile"
          >
            {getUserInitials()}
          </Link>

          {/* Sign Out Button */}
          <button 
            onClick={handleLogout}
            className="btn-secondary-small logout-icon-btn"
            title="Sign Out"
            style={{ borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M10 2v2h3v8h-3v2h5V2h-5zM8.5 4L7 5.5 9.5 8 7 10.5 8.5 12l4-4-4-4zM2 2v12h5v-2H4V4h3V2H2z"/>
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Header;
