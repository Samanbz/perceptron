/**
 * Authentication Context
 * Manages user authentication state across the application
 */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = api.getToken();
      const savedUser = api.getUser();

      if (token && savedUser) {
        // Verify token is still valid
        const isValid = await api.verifyToken();
        if (isValid) {
          setUser(savedUser);
        } else {
          // Token expired, clear auth
          api.logout();
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      console.log('AuthContext: Starting login for:', email);
      const data = await api.login(email, password);
      console.log('AuthContext: Login API response:', data);
      const user = api.getUser();
      console.log('AuthContext: User from localStorage:', user);
      setUser(user);
      return { success: true, user };
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      return { success: false, error: error.message };
    }
  };

  const signup = async (email, name, password) => {
    try {
      await api.signup(email, name, password);
      // Auto login after signup
      const result = await login(email, password);
      return result;
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    navigate('/');
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
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
