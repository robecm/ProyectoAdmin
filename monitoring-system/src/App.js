import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginSignUp from './components/LoginSignUp/LoginSignUp';
import Dashboard from './components/Dashboard/Dashboard';
import Configuration from './components/Configuration/Configuration';
import Graficas from './components/Graficas/Graficas';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={
          !isAuthenticated
            ? <LoginSignUp onLogin={handleLogin} />
            : <Navigate to="/dashboard" />
        } />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route
          path="/config"
          element={isAuthenticated ? <Configuration /> : <Navigate to="/login" />}
        />
        <Route
          path="/graficas"
          element={isAuthenticated ? <Graficas /> : <Navigate to="/login" />}
        />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;