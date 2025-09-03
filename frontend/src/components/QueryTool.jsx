import { useState } from 'react';
import './QueryForm.css';
import './QueryTool.css';
import { createClient } from '@supabase/supabase-js'

// Configura tu cliente de Supabase con tus credenciales
const supabaseUrl = 'https://lcyxhqbafzfudidzzdtm.supabase.co';
//const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxjeXhocWJhZnpmdWRpZHp6ZHRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzMTcxOTAsImV4cCI6MjA2Mzg5MzE5MH0.dS6Gel7N9ze8gDgqHsG7Hisgo3H_v8RjF_Sd8VI86C0'; // ¡No la expongas en producción!
const supabaseKey = import.meta.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

function convertJsonToTable(jsonData, containerId) {
    if (!Array.isArray(jsonData) || jsonData.length === 0) {
        console.error("Invalid JSON data provided.");
        return;
    }

    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container element with ID '${containerId}' not found.`);
        return;
    }

    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Create table header
    const headers = Object.keys(jsonData[0]);
    const headerRow = document.createElement('tr');
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Populate table body
    jsonData.forEach(rowData => {
        const tr = document.createElement('tr');
        headers.forEach(headerText => {
            const td = document.createElement('td');
            td.textContent = rowData[headerText];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    container.innerHTML = ''; // Clear previous content
    container.appendChild(table);
}

function QueryTool() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState('Aquí aparecerán los resultados.');
  const [loading, setLoading] = useState(false);

  const executeQuery = async () => {
    setLoading(true);
    setResults('Cargando...');

    if (!query.trim()) {
      setResults('Por favor, ingresa una consulta SQL.');
      setLoading(false);
      return;
    }

    try {
      // Usa el método .rpc() para llamar a una función SQL en Supabase
      // La función 'execute_sql_query' debe ser una función en tu base de datos
      const { data, error } = await supabase.rpc('execute_sql_query', { query_text: query });

      if (error) {
        throw new Error(error.message);
      }

      if (Array.isArray(data) && data.length > 0) {
        setResults(convertJsonToTable(data, "table-container"));
      } else {
        setResults('Consulta exitosa, pero no se encontraron resultados.');
      }
      
    } catch (error) {
      console.error('Error al ejecutar la consulta:', error);
      setResults(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-form">
      <label className='input-label' htmlFor="queryInput">Ingresa tu consulta SQL:</label>
      <div className="input-group">
        <textarea
            id="queryInput"
            className='question-input'
            placeholder="Ejemplo: SELECT * FROM users;"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
        />
        <button className="submit-button" onClick={executeQuery} disabled={loading}>
            {loading ? 'Ejecutando...' : 'Ejecutar Consulta'}
        </button>
      </div>
      <div className="content-text">
        <h5>Resultado de la API</h5>
        <div id="table-container">
            <pre id="results">
              {results};
            </pre>
        </div> 
      </div>
    </div>
  );
}

export default QueryTool;