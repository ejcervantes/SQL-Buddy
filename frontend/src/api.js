/**
 * Módulo de API para comunicarse con el backend de SQL Query Buddy
 * Configurado para funcionar tanto en desarrollo local como en producción
 */

// Configuración de la API
const API_CONFIG = {
  // URL base del backend - cambiar según el entorno
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // Timeout para las requests
  TIMEOUT: 30000,
  
  // Headers por defecto
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

/**
 * Clase para manejar las llamadas a la API
 */
class ApiClient {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
    this.defaultHeaders = API_CONFIG.DEFAULT_HEADERS;
  }

  /**
   * Realiza una petición HTTP genérica
   * @param {string} endpoint - Endpoint de la API
   * @param {Object} options - Opciones de la petición
   * @returns {Promise<Object>} Respuesta de la API
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config = {
      method: 'GET',
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options
    };

    // Añadir timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    config.signal = controller.signal;

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);

      // Manejar errores HTTP
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          response.status,
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          errorData
        );
      }

      // Parsear respuesta JSON
      const data = await response.json();
      return data;

    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new ApiError(408, 'Request timeout - La petición tardó demasiado');
      }
      
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Error de red u otro tipo
      throw new ApiError(0, `Error de conexión: ${error.message}`);
    }
  }

  /**
   * Realiza una petición GET
   * @param {string} endpoint - Endpoint de la API
   * @param {Object} params - Parámetros de query
   * @returns {Promise<Object>} Respuesta de la API
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, { method: 'GET' });
  }

  /**
   * Realiza una petición POST
   * @param {string} endpoint - Endpoint de la API
   * @param {Object} data - Datos a enviar
   * @returns {Promise<Object>} Respuesta de la API
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  /**
   * Realiza una petición PUT
   * @param {string} endpoint - Endpoint de la API
   * @param {Object} data - Datos a enviar
   * @returns {Promise<Object>} Respuesta de la API
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  /**
   * Realiza una petición DELETE
   * @param {string} endpoint - Endpoint de la API
   * @returns {Promise<Object>} Respuesta de la API
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

/**
 * Clase para manejar errores de la API
 */
class ApiError extends Error {
  constructor(status, message, data = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.timestamp = new Date().toISOString();
  }

  /**
   * Convierte el error a un objeto serializable
   * @returns {Object} Objeto del error
   */
  toJSON() {
    return {
      name: this.name,
      status: this.status,
      message: this.message,
      data: this.data,
      timestamp: this.timestamp
    };
  }
}

// Instancia global del cliente API
const apiClient = new ApiClient();

/**
 * Funciones específicas de la API de SQL Query Buddy
 */

/**
 * Genera una consulta SQL basada en una pregunta
 * @param {string} question - Pregunta en lenguaje natural
 * @returns {Promise<Object>} Respuesta con SQL, explicación y optimización
 */
export async function askQuestion(question) {
  try {
    const response = await apiClient.post('/ask', { question });
    return {
      success: true,
      data: response
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error
    };
  }
}

/**
 * Añade metadatos de una tabla
 * @param {string} tableName - Nombre de la tabla
 * @param {string} schemaInfo - Información del esquema
 * @param {string} description - Descripción de la tabla
 * @returns {Promise<Object>} Respuesta de confirmación
 */
export async function addTableMetadata(tableName, schemaInfo, description) {
  try {
    const response = await apiClient.post('/metadata', {
      table_name: tableName,
      schema_info: schemaInfo,
      description: description
    });
    return {
      success: true,
      data: response
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error
    };
  }
}

/**
 * Obtiene la lista de tablas disponibles
 * @returns {Promise<Object>} Lista de tablas
 */
export async function getTables() {
  try {
    const response = await apiClient.get('/tables');
    return {
      success: true,
      data: response
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error
    };
  }
}

/**
 * Verifica el estado de salud de la API
 * @returns {Promise<Object>} Estado de salud
 */
export async function checkHealth() {
  try {
    const response = await apiClient.get('/health');
    return {
      success: true,
      data: response
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error
    };
  }
}

/**
 * Obtiene información básica de la API
 * @returns {Promise<Object>} Información de la API
 */
export async function getApiInfo() {
  try {
    const response = await apiClient.get('/');
    return {
      success: true,
      data: response
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error
    };
  }
}

// Exportar el cliente API y las funciones
export { apiClient, ApiError };
export default apiClient;
