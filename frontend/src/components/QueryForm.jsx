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
        <div className="query-form-subtitle">
          The deployed application simulates the database of a convenience store. It currently has
          3 tables, so the AI can only answer questions related to these tables; otherwise
          it will not be able to generate a proper SQL query due to lack of context.
          <ul>
            <li>Customers: This table stores information about the company's customers. It contains personal data such as name and email, the date they registered, and their country of origin.</li>
            <li>Products: This table contains information about the store's products, with values such as price, stock, and category.</li>
            <li>Sales: This table contains information about the store's orders, with data such as the order, the product, the date, and the total purchase.</li>
          </ul>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-group">
          <label htmlFor="question" className="input-label">
            What do you want to query?
          </label>
          
          <div className="input-wrapper">
            <textarea
              id="question"
              name="question"
              value={question}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="E.g.: How many users registered last month?"
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
                  The question cannot be empty
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
                Generating SQL...
              </>
            ) : (
              <>
                <span className="button-icon">⚡</span>
                Generate SQL
              </>
            )}
          </button>
        </div>
      </form>

      <div className="query-form-examples">
        <h3 className="examples-title">💡 Example questions:</h3>
        <div className="examples-grid">
          <button
            className="example-button"
            onClick={() => setQuestion('How many customers are there in total?')}
            disabled={isLoading}
          >
            How many customers are there in total?
          </button>

          <button
            className="example-button"
            onClick={() => setQuestion('Show the best-selling products of the month')}
            disabled={isLoading}
          >
            Show the best-selling products of the month
          </button>

          <button
            className="example-button"
            onClick={() => setQuestion('Find customers who have not placed orders')}
            disabled={isLoading}
          >
            Find customers who have not placed orders
          </button>

          <button
            className="example-button"
            onClick={() => setQuestion('Calculate total sales by category')}
            disabled={isLoading}
          >
            Calculate total sales by category
          </button>
        </div>
      </div>
    </div>
  );
};

export default QueryForm;
