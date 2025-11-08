import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Signup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signup } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      console.log('Signup attempt:', { email: formData.email, name: formData.name });
      const result = await signup(formData.email, formData.name, formData.password);
      console.log('Signup result:', result);
      
      if (result.success) {
        // Redirect to dashboard on successful signup
        navigate('/dashboard');
      } else {
        setError(result.error || 'Signup failed. Please try again.');
      }
    } catch (err) {
      console.error('Signup error:', err);
      setError(`Network error: ${err.message}. Please check if the backend server is running.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container-split">
      <div className="auth-left">
        <div className="auth-form-wrapper">
          <div className="auth-header">
            <div className="auth-logo">
              <img src="/logo_solo.png" alt="Perceptron" className="auth-logo-image" />
              <span className="logo-text">Perceptron</span>
            </div>
            <h1>Create Account</h1>
            <p>Join the future of intelligence analytics</p>
          </div>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@company.com"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                required
                disabled={loading}
                minLength="8"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                required
                disabled={loading}
              />
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input type="checkbox" required disabled={loading} />
                <span>I agree to the <Link to="/terms" className="auth-link">Terms of Service</Link> and <Link to="/privacy" className="auth-link">Privacy Policy</Link></span>
              </label>
            </div>

            <button 
              type="submit" 
              className="btn-primary btn-full"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="auth-link">Sign in</Link>
            </p>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-visual">
          <img src="/logo_solo.png" alt="Perceptron Intelligence" className="auth-visual-logo" />
          <h2>Transform Data into Intelligence</h2>
          <p>Join thousands of professionals using Perceptron to make data-driven decisions with AI-powered intelligence teams.</p>
          <div className="auth-features">
            <div className="auth-feature">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <h4>Real-time Analysis</h4>
                <p>Process millions of data points instantly</p>
              </div>
            </div>
            <div className="auth-feature">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <h4>AI Intelligence Teams</h4>
                <p>Specialized agents for every domain</p>
              </div>
            </div>
            <div className="auth-feature">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <h4>Enterprise Security</h4>
                <p>Bank-grade encryption and compliance</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Signup;
