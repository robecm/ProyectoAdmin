import React from "react";
import "./Graficas.css";

// Importación de las imágenes desde la carpeta src/assets
import Grafica1 from './assets/Grafica1.jpeg';
import Grafica2 from './assets/Grafica2.jpeg';
import Grafica3 from './assets/Grafica3.jpeg';

// Definir las imágenes con sus títulos y rutas
const imagenes = [
  { id: 1, titulo: "Gráfica 1", url: Grafica1 },
  { id: 2, titulo: "Gráfica 2", url: Grafica2 },
  { id: 3, titulo: "Gráfica 3", url: Grafica3 },
];

function Graficas() {
  return (
    <div className="app-container">
      <header className="header">
        <h1>Galería de Gráficas</h1>
        <p>Visualización de los datos</p>
      </header>

      <div className="grid-container">
        {imagenes.map((img) => (
          <div className="card" key={img.id}>
            <img src={img.url} alt={img.titulo} className="grafica-img" />
            <h2 className="grafica-titulo">{img.titulo}</h2>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Graficas;
