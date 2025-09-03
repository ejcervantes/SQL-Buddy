import React, { useState, useEffect } from 'react';
import QueryForm from './components/QueryForm';
import ResultCard from './components/ResultCard';
import { askQuestion, checkHealth } from './api';
import './App.css';

/**
 * Componente principal de la aplicación SQL Query Buddy (RAG)
 * Maneja el estado global y la lógica de la aplicación
 */
function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [lastQuestion, setLastQuestion] = useState('');

  /**
   * Verifica el estado de la API al cargar la aplicación
   */
  useEffect(() => {
    checkApiHealth();
  }, []);

  /**
   * Verifica la salud de la API
   */
  const checkApiHealth = async () => {
    try {
      setApiStatus('checking');
      const response = await checkHealth();
      
      if (response.success) {
        setApiStatus('healthy');
      } else {
        setApiStatus('error');
        console.error('API Health Check failed:', response.error);
      }
    } catch (err) {
      setApiStatus('error');
      console.error('API Health Check error:', err);
    }
  };

  /**
   * Maneja el envío de una nueva pregunta
   * @param {string} question - Pregunta del usuario
   */
  const handleSubmitQuestion = async (question) => {
    try {
      setIsLoading(true);
      setError(null);
      setResult(null);
      setLastQuestion(question);

      console.log('Enviando pregunta:', question);

      const response = await askQuestion(question);

      if (response.success) {
        setResult(response.data);
        console.log('Respuesta recibida:', response.data);
      } else {
        setError(response.error || 'Error desconocido al generar SQL');
        console.error('Error en la respuesta:', response);
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
      console.error('Error al enviar pregunta:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Maneja la solicitud de una nueva consulta
   */
  const handleNewQuery = () => {
    setResult(null);
    setError(null);
    setLastQuestion('');
  };

  /**
   * Renderiza el banner de estado de la API
   */
  const renderApiStatusBanner = () => {
    if (apiStatus === 'checking') {
      return (
        <div className="api-status-banner checking">
          <span className="status-icon">⏳</span>
          Verificando conexión con el servidor...
        </div>
      );
    }

    if (apiStatus === 'error') {
      return (
        <div className="api-status-banner error">
          <span className="status-icon">❌</span>
          No se pudo conectar con el servidor
          <button 
            className="retry-button"
            onClick={checkApiHealth}
          >
            Reintentar
          </button>
        </div>
      );
    }

    if (apiStatus === 'healthy') {
      return (
        <div className="api-status-banner healthy">
          <span className="status-icon">✅</span>
          Conectado al servidor
        </div>
      );
    }

    return null;
  };

  /**
   * Renderiza el mensaje de error
   */
  const renderError = () => {
    if (!error) return null;

    return (
      <div className="error-message fade-in">
        <div className="error-header">
          <span className="error-icon">⚠️</span>
          <h3>Error al generar SQL</h3>
        </div>
        <p className="error-text">{error}</p>
        <button 
          className="retry-button"
          onClick={() => handleSubmitQuestion(lastQuestion)}
        >
          Reintentar
        </button>
      </div>
    );
  };

  return (
    <div className="app">
      {/* Banner de estado de la API */}
      {renderApiStatusBanner()}

      {/* Contenido principal */}
      <main className="app-main">
        <div className="container">
          {/* Formulario de consulta */}
          <QueryForm 
            onSubmit={handleSubmitQuestion}
            isLoading={isLoading}
          />

          {/* Mensaje de error */}
          {renderError()}

          {/* Resultados */}
          {result && (
            <ResultCard
              result={result}
              question={lastQuestion}
              onNewQuery={handleNewQuery}
            />
          )}

          {/* Estado de carga */}
          {isLoading && (
            <div className="loading-state fade-in">
              <div className="loading-content">
                <div className="loading-spinner"></div>
                <h3>Generando consulta SQL...</h3>
                <p>Esto puede tomar unos segundos</p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          <p className="footer-text">
            SQL Query Buddy (RAG) - Genera consultas SQL usando inteligencia artificial
          </p>
          <div className="footer-links">
            <a 
              href="https://github.com/ejcervantes/SQL-Buddy"
              target="_blank" 
              rel="noopener noreferrer"
              className="footer-link"
            >
              GitHub - Source Code
            </a>
            <span className="footer-separator">•</span>
            <a 
              href="https://platform.openai.com/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="footer-link"
            >
              OpenAI API
            </a>
            <span className="footer-separator">•</span>
            <a 
              href="https://www.trychroma.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="footer-link"
            >
              ChromaDB
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
