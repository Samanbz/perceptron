import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-logo-column">
          <img src="/logo_solo.png" alt="Perceptron" className="footer-logo-image" />
        </div>
        <div className="footer-column">
          <h4>Product</h4>
          <Link to="/features">Features</Link>
          <Link to="/teams">Intelligence Teams</Link>
          <Link to="/technology">Technology</Link>
          <a href="#pricing">Pricing</a>
        </div>
        <div className="footer-column">
          <h4>Developers</h4>
          <Link to="/documentation">Documentation</Link>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Reference</a>
          <a href="#sdk">SDK</a>
        </div>
        <div className="footer-column">
          <h4>Company</h4>
          <a href="#about">About</a>
          <a href="#blog">Blog</a>
          <a href="#careers">Careers</a>
        </div>
      </div>
      <div className="footer-bottom">
        <p className="footer-copyright">&copy; 2025 Perceptron. All rights reserved.</p>
        <div className="footer-legal-links">
          <Link to="/privacy">Privacy Policy</Link>
          <Link to="/terms">Terms of Service</Link>
          <Link to="/cookies">Cookie Policy</Link>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
