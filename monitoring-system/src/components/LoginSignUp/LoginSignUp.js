import React, { useState } from 'react';
import './LoginSignUp.css';

function LoginSignUp({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, you would verify credentials
    // For now, just simulate successful login
    onLogin();
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>{isSignup ? 'Crear Cuenta' : 'Iniciar Sesión'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              placeholder="Usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="login-button">
            {isSignup ? 'Registrarse' : 'Ingresar'}
          </button>
        </form>
        <p>
          {isSignup
            ? '¿Ya tienes cuenta?'
            : '¿No tienes cuenta?'}
          <span onClick={() => setIsSignup(!isSignup)}>
            {isSignup ? 'Iniciar sesión' : 'Regístrate'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default LoginSignUp;