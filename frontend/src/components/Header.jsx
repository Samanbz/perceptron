import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showUserMenu && !e.target.closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showUserMenu]);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  const getUserInitials = () => {
    if (!user || !user.name) return 'U';
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
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Home
          </Link>
          <Link 
            to="/features" 
            className={`nav-link ${location.pathname === '/features' ? 'active' : ''}`}
          >
            Features
          </Link>
          <Link 
            to="/pricing" 
            className={`nav-link ${location.pathname === '/pricing' ? 'active' : ''}`}
          >
            Pricing
          </Link>
        </div>

        {/* Auth Buttons / User Menu */}
        <div className="nav-auth">
          {isAuthenticated ? (
            <>
              {/* Logout Button */}
              <button 
                onClick={handleLogout}
                className="btn-secondary-small"
                title="Sign Out"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style={{ marginRight: '4px' }}>
                  <path d="M10 2v2h3v8h-3v2h5V2h-5zM8.5 4L7 5.5 9.5 8 7 10.5 8.5 12l4-4-4-4zM2 2v12h5v-2H4V4h3V2H2z"/>
                </svg>
                Sign Out
              </button>

              {/* User Avatar */}
              <div className="user-menu-container">
                <button 
                  className="user-avatar"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  title={user?.name || 'User Menu'}
                >
                  {getUserInitials()}
                </button>

                {showUserMenu && (
                  <div className="user-dropdown">
                    <div className="user-dropdown-header">
                      <div className="user-avatar-large">{getUserInitials()}</div>
                      <div className="user-info">
                        <div className="user-name">{user?.name || 'User'}</div>
                        <div className="user-email">{user?.email || ''}</div>
                      </div>
                    </div>
                    <div className="user-dropdown-divider"></div>
                    <Link 
                      to="/dashboard" 
                      className="user-dropdown-item"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M2 4h12v2H2V4zm0 4h12v2H2V8zm0 4h12v2H2v-2z"/>
                      </svg>
                      Dashboard
                    </Link>
                    <Link 
                      to="/pricing" 
                      className="user-dropdown-item"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 2C4.686 2 2 4.686 2 8s2.686 6 6 6 6-2.686 6-6-2.686-6-6-6zm0 10c-2.206 0-4-1.794-4-4s1.794-4 4-4 4 1.794 4 4-1.794 4-4 4z"/>
                      </svg>
                      Upgrade Plan
                    </Link>
                    <div className="user-dropdown-divider"></div>
                    <button 
                      className="user-dropdown-item logout"
                      onClick={handleLogout}
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M10 2v2h3v8h-3v2h5V2h-5zM8.5 4L7 5.5 9.5 8 7 10.5 8.5 12l4-4-4-4zM2 2v12h5v-2H4V4h3V2H2z"/>
                      </svg>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary-small">
                Login
              </Link>
              <Link to="/signup" className="btn-primary-small">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Header;
