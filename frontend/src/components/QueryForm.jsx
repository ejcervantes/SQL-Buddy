import React, { useState } from 'react';
import './QueryForm.css';
import myLogo from '../img/Logo HAYIBA.png';
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
          <img src={myLogo} alt='Logo' className='query-form-title-img'></img>  SQL Query Buddy (RAG)
        </h2>
        <p className="query-form-subtitle">
          La aplicación desplegada simula la base de datos de una tienda por conveniencia. Por el momento cuenta con 
          3 tablas, por lo que la IA unicamente podrá responder preguntas relacionadas a estas tablas, de otra 
          forma no podrá generar una consulta SQL adecuada por falta de contexto.
          <ul>
            <li>Clientes: Esta tabla almacena información sobre los clientes de la empresa. Contiene datos personales como nombre y email, la fecha en que se registraron y su país de origen.</li>
            <li>Productos: Esta tabla contiene información de los productos de la tienda, con valores como precio, stock y categoria.</li>
            <li>Ventas: La tabla contiene información de los pedidos de la tienda, con información como el pedido, el producto, la fecha y compra total.</li>
          </ul>
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
