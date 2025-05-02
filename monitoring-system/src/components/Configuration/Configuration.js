import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "./Configuration.css";

function Configuration() {
  const navigate = useNavigate();

  // Estado para Configuración General
  const [configGeneral, setConfigGeneral] = useState({
    nombreSistema: "Monitoreo Inteligente",
    ubicacionTienda: "",
    zonaHoraria: "UTC-6",
    formatoHora: "24h",
  });

  // Estado para Configuración de Cámaras
  const [camaras, setCamaras] = useState([]);
  const [nuevaCamara, setNuevaCamara] = useState("");
  const [sensibilidad, setSensibilidad] = useState(5);
  const [frecuencia, setFrecuencia] = useState("10s");
  const [zonasInteres, setZonasInteres] = useState("");

  // Estado para Configuración de Reportes
  const [configReportes, setConfigReportes] = useState({
    frecuencia: "diario",
    analisis: {
      horariosAfluencia: false,
      comparacionDias: false,
      clientesPasillo: false,
    },
  });

  // Función para actualizar Configuración General
  const handleChangeGeneral = (e) => {
    const { name, value } = e.target;
    setConfigGeneral({ ...configGeneral, [name]: value });
  };

  // Función para manejar cambios en Configuración de Reportes
  const handleChangeReportes = (e) => {
    const { name, checked } = e.target;
    setConfigReportes({
      ...configReportes,
      analisis: { ...configReportes.analisis, [name]: checked },
    });
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <div className="config-page">
      <div className="header">
        <button onClick={handleBackToDashboard}>← Volver al Dashboard</button>
        <div className="title">Configuración</div>
        <div></div>
      </div>

      <div className="container">
        <div className="header">
          <div className="text">Configuración del Sistema</div>
          <div className="underline"></div>
        </div>

        {/* Configuración General */}
        <div className="section">
          <h2>Configuración General</h2>
          <div className="input-group">
            <input type="text" name="nombreSistema" value={configGeneral.nombreSistema} onChange={handleChangeGeneral} placeholder="Nombre del Sistema" />
          </div>
          <div className="input-group">
            <select name="ubicacionTienda" value={configGeneral.ubicacionTienda} onChange={handleChangeGeneral}>
              <option value="">Ubicación de la Tienda</option>
              <option value="CDMX">CDMX</option>
              <option value="Guadalajara">Guadalajara</option>
              <option value="Monterrey">Monterrey</option>
            </select>
          </div>
          <div className="input-group">
            <select name="zonaHoraria" value={configGeneral.zonaHoraria} onChange={handleChangeGeneral}>
              <option value="UTC-6">UTC-6</option>
              <option value="UTC-5">UTC-5</option>
              <option value="UTC-7">UTC-7</option>
            </select>
          </div>
          <div className="input-group">
            <select name="formatoHora" value={configGeneral.formatoHora} onChange={handleChangeGeneral}>
              <option value="12h">12 Horas</option>
              <option value="24h">24 Horas</option>
            </select>
          </div>
        </div>

        {/* Resto del código de configuración igual que en App.js original */}
        <div className="section">
          <h2>Configuración de Cámaras</h2>
          <div className="input-group">
            <input type="text" placeholder="Nombre de la nueva cámara" value={nuevaCamara} onChange={(e) => setNuevaCamara(e.target.value)} />
            <button className="submit" onClick={() => setCamaras([...camaras, { id: Date.now(), nombre: nuevaCamara }])}>Agregar Cámara</button>
          </div>
          <ul>
            {camaras.map((cam) => (
              <li key={cam.id}>{cam.nombre} <button onClick={() => setCamaras(camaras.filter(c => c.id !== cam.id))}>Eliminar</button></li>
            ))}
          </ul>
          <div className="input-group">
            <label>Sensibilidad de Detección</label>
            <input type="range" min="1" max="10" value={sensibilidad} onChange={(e) => setSensibilidad(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Frecuencia de Actualización</label>
            <select value={frecuencia} onChange={(e) => setFrecuencia(e.target.value)}>
              <option value="5s">Cada 5 segundos</option>
              <option value="10s">Cada 10 segundos</option>
              <option value="30s">Cada 30 segundos</option>
            </select>
          </div>
          <div className="input-group">
            <input type="text" placeholder="Zonas de interés" value={zonasInteres} onChange={(e) => setZonasInteres(e.target.value)} />
          </div>
        </div>

        <div className="section">
          <h2>Configuración de Reportes</h2>
          <div className="input-group">
            <select value={configReportes.frecuencia} onChange={(e) => setConfigReportes({ ...configReportes, frecuencia: e.target.value })}>
              <option value="diario">Diario</option>
              <option value="semanal">Semanal</option>
              <option value="mensual">Mensual</option>
            </select>
          </div>
          <div className="input-group">
            <label><input type="checkbox" name="horariosAfluencia" checked={configReportes.analisis.horariosAfluencia} onChange={handleChangeReportes} /> Horarios de mayor afluencia</label>
            <label><input type="checkbox" name="comparacionDias" checked={configReportes.analisis.comparacionDias} onChange={handleChangeReportes} /> Comparación con días anteriores</label>
            <label><input type="checkbox" name="clientesPasillo" checked={configReportes.analisis.clientesPasillo} onChange={handleChangeReportes} /> Promedio de clientes por pasillo</label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Configuration;