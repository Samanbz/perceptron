/**
 * API Service for backend communication
 * Handles authentication and HTTP requests
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Get auth token from localStorage
  getToken() {
    return localStorage.getItem('auth_token');
  }

  // Set auth token in localStorage
  setToken(token) {
    localStorage.setItem('auth_token', token);
  }

  // Remove auth token from localStorage
  removeToken() {
    localStorage.removeItem('auth_token');
  }

  // Get user data from localStorage
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  // Set user data in localStorage
  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  }

  // Remove user data from localStorage
  removeUser() {
    localStorage.removeItem('user');
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Make HTTP request with authentication
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Add authorization header if token exists
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication endpoints
  async signup(email, name, password) {
    const data = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    });

    return data;
  }

  async login(email, password) {
    try {
      console.log('Attempting login for:', email);
      const data = await this.request('/auth/login/json', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      console.log('Login response:', data);

      // Store token and fetch user info
      if (data.access_token) {
        this.setToken(data.access_token);
        console.log('Token stored, fetching user info...');
        
        try {
          const user = await this.getCurrentUser();
          console.log('User info fetched:', user);
          this.setUser(user);
          return { success: true, user, token: data.access_token };
        } catch (userError) {
          console.error('Error fetching user info:', userError);
          // Token is valid but couldn't fetch user, still allow login
          return { success: true, token: data.access_token };
        }
      }

      return { success: false, error: 'No access token received' };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async getCurrentUser() {
    const data = await this.request('/auth/me');
    return data;
  }

  async verifyToken() {
    try {
      const data = await this.request('/auth/verify');
      return data.valid;
    } catch (error) {
      return false;
    }
  }

  logout() {
    this.removeToken();
    this.removeUser();
  }

  // Health check
  async healthCheck() {
    const data = await this.request('/api/health');
    return data;
  }
}

export default new ApiService();
