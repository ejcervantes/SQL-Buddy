import React, { useState } from 'react';
import './ResultCard.css';
import QueryTool from './QueryTool';

/**
 * Componente para mostrar los resultados de la consulta SQL generada
 * Incluye el SQL, explicación y sugerencias de optimización
 */
const ResultCard = ({ result, question, onNewQuery }) => {
  const [activeTab, setActiveTab] = useState('sql');
  const [copied, setCopied] = useState(false);

  if (!result) {
    return null;
  }

  /**
   * Copia el SQL al portapapeles
   */
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(result.sql_query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Error copiando al portapapeles:', err);
    }
  };

  /**
   * Formatea el SQL para mejor legibilidad
   */
  const formatSQL = (sql) => {
    if (!sql) return '';
    
    // Añadir resaltado básico para palabras clave SQL
    const keywords = [
      'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
      'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'ON',
      'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS NULL',
      'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT', 'CASE', 'WHEN',
      'THEN', 'ELSE', 'END', 'UNION', 'ALL'
    ];
    
    let formatted = sql;
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      formatted = formatted.replace(regex, `<span class="sql-keyword">${keyword}</span>`);
    });
    
    return formatted;
  };

  /**
   * Maneja el cambio de pestaña
   */
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="result-card fade-in">
      <div className="result-header">
        <div className="result-question">
          <h3 className="question-text">{question}</h3>
        </div>
        
        <button 
          className="new-query-button"
          onClick={onNewQuery}
        >
          <span className="button-icon">🔄</span>
          New Query
        </button>
      </div>

      <div className="result-tabs">
        <button
          className={`tab-button ${activeTab === 'sql' ? 'active' : ''}`}
          onClick={() => handleTabChange('sql')}
        >
          <span className="tab-icon">💻</span>
          Generated SQL
        </button>
        
        <button
          className={`tab-button ${activeTab === 'explanation' ? 'active' : ''}`}
          onClick={() => handleTabChange('explanation')}
        >
          <span className="tab-icon">📖</span>
          Explanation
        </button>
        
        <button
          className={`tab-button ${activeTab === 'optimization' ? 'active' : ''}`}
          onClick={() => handleTabChange('optimization')}
        >
          <span className="tab-icon">⚡</span>
          Optimization
        </button>

        <button
          className={`tab-button ${activeTab === 'sqltool' ? 'active' : ''}`}
          onClick={() => handleTabChange('querytry')}
        >
          <span className="tab-icon">📊</span>
          Test Query
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'sql' && (
          <div className="sql-content">
            <div className="sql-header">
              <h4 className="content-title">Generated SQL Query</h4>
              <button
                className={`copy-button ${copied ? 'copied' : ''}`}
                onClick={copyToClipboard}
                title="Copy SQL"
              >
                {copied ? (
                  <>
                    <span className="copy-icon">✅</span>
                    Copied
                  </>
                ) : (
                  <>
                    <span className="copy-icon">📋</span>
                    Copy
                  </>
                )}
              </button>
            </div>
            
            <div className="sql-code">
              <pre className="sql-pre">
                <code 
                  className="sql-code-content"
                  dangerouslySetInnerHTML={{ __html: formatSQL(result.sql_query) }}
                />
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'explanation' && (
          <div className="explanation-content">
            <h4 className="content-title">What does this query do?</h4>
            <div className="content-text">
              <p>{result.explanation}</p>
            </div>
          </div>
        )}

        {activeTab === 'optimization' && (
          <div className="optimization-content">
            <h4 className="content-title">Optimization Suggestions</h4>
            <div className="content-text">
              <p>{result.optimization}</p>
            </div>
          </div>
        )}

        {activeTab === 'querytry' && (
          <div className="querytry-content">
            <h4 className="querytry-title">Query Test</h4>
            <div className="querytool-container">
              <QueryTool />
            </div>
          </div>
        )}
      </div>

      <div className="result-footer">
        <div className="result-meta">
          <span className="meta-item">
            <span className="meta-icon">🤖</span>
            Generated with AI
          </span>
          <span className="meta-item">
            <span className="meta-icon">⏱️</span>
            {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;
