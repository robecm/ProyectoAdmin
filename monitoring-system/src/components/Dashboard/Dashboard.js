import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import userIcon from '../../assets/img/usuario.png';
import settingsIcon from '../../assets/img/engranaje.png';
import recIcon from '../../assets/img/rec.png';

function Dashboard() {
  const navigate = useNavigate();
  const [personCounts, setPersonCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const countTimerRef = useRef(null);
  const streamUrlsRef = useRef({});
  const streamRefs = useRef([]);

  useEffect(() => {
    setLoading(true);
    const urls = {};
    for (let i = 0; i < 9; i++) {
      const cameraId = `camera_${i + 1}`;
      urls[cameraId] = `http://localhost:5000/video_feed/${cameraId}`;
    }
    streamUrlsRef.current = urls;
    streamRefs.current = Array(9).fill(null);
    fetch('http://localhost:5000/status')
      .then(() => setLoading(false))
      .catch(err => {
        console.error("Error connecting to server:", err);
        setLoading(false);
      });
    return () => {
      streamRefs.current.forEach(img => {
        if (img) {
          img.src = '';
          img.onload = null;
          img.onerror = null;
        }
      });
    };
  }, []);

  useEffect(() => {
    countTimerRef.current = setInterval(() => {
      fetch('http://localhost:5000/detection_counts')
        .then(response => response.json())
        .then(data => setPersonCounts(data))
        .catch(error => console.error('Error fetching counts:', error));
    }, 1000);

    return () => {
      if (countTimerRef.current) clearInterval(countTimerRef.current);
    };
  }, []);

  const handleSettingsClick = () => {
    streamRefs.current.forEach(img => {
      if (img) img.src = '';
    });
    navigate('/config');
  };

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="loading-text">Cargando cámaras...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="header">
        <div className="left-panel">
          <img src={userIcon} alt="Usuario" className="user-icon" />
        </div>
        <div className="title">Cámaras</div>
        <div className="right-panel">
          <img
            src={settingsIcon}
            alt="Ajustes"
            className="settings-icon"
            onClick={handleSettingsClick}
          />
        </div>
      </div>

      <div className="cameras-grid">
        {Array.from({length: 9}, (_, i) => {
          const cameraId = `camera_${i + 1}`;
          const count = personCounts[cameraId] || 0;
          const streamUrl = streamUrlsRef.current[cameraId] || '';

          return (
            <div className="camera" key={i}>
              <div className="camera-label">Cámara {i + 1}</div>
              <img
                className="camera-feed"
                src={streamUrl}
                alt={`Camera feed ${i + 1}`}
                ref={el => streamRefs.current[i] = el}
                onError={(e) => {
                  e.target.onerror = null;
                  if (e.target) e.target.src = streamUrl;
                }}
              />
              <img className="rec-icon" src={recIcon} alt="REC" />
              <div className="rec-indicator">REC</div>
              <div className="person-count">Personas: {count}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Dashboard;