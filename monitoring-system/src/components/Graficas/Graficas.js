// monitoring-system/src/components/Graficas/Graficas.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Graficas.css';

function Graficas() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // Generate mock data for charts
    const generateData = () => {
      return {
        hourlyData: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          count: Math.floor(Math.random() * 80) + 10
        })),
        cameraData: Array.from({ length: 9 }, (_, i) => ({
          camera: `Cámara ${i+1}`,
          count: Math.floor(Math.random() * 100) + 5,
          color: `hsl(${i * 40}, 70%, 60%)`
        })),
        weeklyData: Array.from({ length: 7 }, (_, i) => {
          const days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
          return {
            day: days[i],
            count: Math.floor(Math.random() * 150) + 30
          };
        })
      };
    };

    // Simulate data loading
    const timer = setTimeout(() => {
      setChartData(generateData());
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleBackToConfig = () => {
    navigate('/config');
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  // Get the maximum value for scaling
  const getMaxValue = (data, key) => {
    return Math.max(...data.map(item => item[key])) * 1.2;
  };

  return (
    <div className="graficas-page">
      <div className="graficas-header">
        <button onClick={handleBackToConfig}>← Volver a Configuración</button>
        <div className="graficas-title">Gráficas y Estadísticas</div>
        <button onClick={handleBackToDashboard}>Ir al Dashboard</button>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando datos de análisis...</p>
        </div>
      ) : (
        <div className="charts-container">
          <div className="chart-section">
            <h2>Afluencia por Hora</h2>
            <div className="chart-placeholder">
              <div className="bar-chart">
                {chartData.hourlyData.map((item, i) => (
                  <div
                    key={i}
                    className="bar-container"
                  >
                    <div
                      className="bar"
                      style={{
                        height: `${(item.count / getMaxValue(chartData.hourlyData, 'count')) * 180}px`
                      }}
                    >
                      <span className="bar-value">{item.count}</span>
                    </div>
                    <div className="bar-label">{item.hour}h</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="chart-section">
            <h2>Personas por Cámara</h2>
            <div className="chart-placeholder">
              <div className="camera-distribution">
                {chartData.cameraData.map((item, i) => (
                  <div key={i} className="camera-stat">
                    <div className="camera-bar-container">
                      <div
                        className="camera-bar"
                        style={{
                          width: `${(item.count / getMaxValue(chartData.cameraData, 'count')) * 100}%`,
                          backgroundColor: item.color
                        }}
                      ></div>
                      <span className="camera-count">{item.count}</span>
                    </div>
                    <div className="camera-label">{item.camera}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="chart-section">
            <h2>Comparativa Semanal</h2>
            <div className="chart-placeholder">
              <div className="line-chart">
                <div className="line-path"></div>
                {chartData.weeklyData.map((item, i) => (
                  <div
                    key={i}
                    className="line-point"
                    style={{
                      left: `${(i / (chartData.weeklyData.length - 1)) * 100}%`,
                      bottom: `${(item.count / getMaxValue(chartData.weeklyData, 'count')) * 80}%`
                    }}
                    data-value={item.count}
                  >
                    <div className="point-tooltip">{item.day}: {item.count}</div>
                  </div>
                ))}

                <div className="chart-labels">
                  {chartData.weeklyData.map((item, i) => (
                    <div
                      key={i}
                      className="day-label"
                      style={{ left: `${(i / (chartData.weeklyData.length - 1)) * 100}%` }}
                    >
                      {item.day}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Graficas;