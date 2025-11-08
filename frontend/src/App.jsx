import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/Header';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Features from './pages/Features';
import Pricing from './pages/Pricing';
import Teams from './pages/Teams';
import Technology from './pages/Technology';
import Documentation from './pages/Documentation';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import Cookies from './pages/Cookies';
import Dashboard from './pages/Dashboard';
import PeersNewsroom from './pages/PeersNewsroom';
import ReputationMap from './pages/ReputationMap';
import Profile from './pages/Profile';
import './App.css';

function AppContent() {
  return (
    <div className="app">
      <Header />
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/features" element={<Features />} />
        <Route path="/peers-newsroom" element={<PeersNewsroom />} />
        <Route path="/reputation-map" element={<ReputationMap />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/teams" element={<Teams />} />
        <Route path="/technology" element={<Technology />} />
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/cookies" element={<Cookies />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
      </Routes>

      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
