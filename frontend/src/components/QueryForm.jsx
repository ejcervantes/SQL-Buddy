import React, { useState } from 'react';
import './QueryForm.css';

/**
 * Componente del formulario para hacer preguntas al sistema
 * Permite al usuario escribir preguntas en lenguaje natural
 */
const QueryForm = ({ onSubmit, isLoading = false }) => {
  const [question, setQuestion] = useState('');
  const [isValid, setIsValid] = useState(true);

  /**
   * Valida que la pregunta no esté vacía
   * @param {string} value - Valor a validar
   * @returns {boolean} True si es válido
   */
  const validateQuestion = (value) => {
    const trimmed = value.trim();
    return trimmed.length > 0 && trimmed.length <= 500;
  };

  /**
   * Maneja el cambio en el input
   * @param {Event} e - Evento del input
   */
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuestion(value);
    setIsValid(validateQuestion(value));
  };

  /**
   * Maneja el envío del formulario
   * @param {Event} e - Evento del formulario
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateQuestion(question)) {
      setIsValid(false);
      return;
    }

    onSubmit(question.trim());
  };

  /**
   * Maneja la tecla Enter en el input
   * @param {Event} e - Evento del input
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="query-form-container">
      <div className="query-form-header">
        <h2 className="query-form-title">
          🤖 SQL Query Buddy (RAG)
        </h2>
        <p className="query-form-subtitle">
          Escribe tu pregunta en lenguaje natural y obtén consultas SQL optimizadas
        </p>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-group">
          <label htmlFor="question" className="input-label">
            ¿Qué quieres consultar?
          </label>
          
          <div className="input-wrapper">
            <textarea
              id="question"
              name="question"
              value={question}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Ej: ¿Cuántos usuarios se registraron en el último mes?"
              className={`question-input ${!isValid ? 'error' : ''}`}
              rows="3"
              maxLength="500"
              disabled={isLoading}
            />
            
            <div className="input-footer">
              <span className={`char-count ${question.length > 450 ? 'warning' : ''}`}>
                {question.length}/500
              </span>
              
              {!isValid && (
                <span className="error-message">
                  La pregunta no puede estar vacía
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className={`submit-button ${isLoading ? 'loading' : ''}`}
            disabled={!isValid || isLoading || question.trim().length === 0}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Generando SQL...
              </>
            ) : (
              <>
                <span className="button-icon">⚡</span>
                Generar SQL
              </>
            )}
          </button>
        </div>
      </form>

      <div className="query-form-examples">
        <h3 className="examples-title">💡 Ejemplos de preguntas:</h3>
        <div className="examples-grid">
          <button
            className="example-button"
            onClick={() => setQuestion('¿Cuántos usuarios hay en total?')}
            disabled={isLoading}
          >
            ¿Cuántos usuarios hay en total?
          </button>
          
          <button
            className="example-button"
            onClick={() => setQuestion('Muestra los productos más vendidos del mes')}
            disabled={isLoading}
          >
            Muestra los productos más vendidos del mes
          </button>
          
          <button
            className="example-button"
            onClick={() => setQuestion('Encuentra clientes que no han hecho pedidos')}
            disabled={isLoading}
          >
            Encuentra clientes que no han hecho pedidos
          </button>
          
          <button
            className="example-button"
            onClick={() => setQuestion('Calcula el total de ventas por categoría')}
            disabled={isLoading}
          >
            Calcula el total de ventas por categoría
          </button>
        </div>
      </div>
    </div>
  );
};

export default QueryForm;
