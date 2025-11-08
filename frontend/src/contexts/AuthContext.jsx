/**
 * Authentication Context
 * Manages user authentication state across the application
 */
import React, { createContext, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Mock user - always logged in mode
  const [user] = useState({
    name: 'Demo User',
    email: 'demo@perceptron.ai',
    id: 'demo-user-123'
  });
  const [loading] = useState(false);
  const navigate = useNavigate();

  const login = async (email, password) => {
    try {
      console.log('AuthContext: Starting login for:', email);
      const data = await api.login(email, password);
      console.log('AuthContext: Login API response:', data);
      return { success: true, user };
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      return { success: false, error: error.message };
    }
  };

  const signup = async (email, name, password) => {
    try {
      await api.signup(email, name, password);
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    api.logout();
    navigate('/');
  };

  const value = {
    user,
    loading,
    isAuthenticated: true, // Always authenticated in mock mode
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
