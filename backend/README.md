# SQL Query Buddy (RAG) - Backend

Backend de FastAPI para generar consultas SQL usando RAG (Retrieval Augmented Generation) con ChromaDB y OpenAI GPT.

## 🚀 Características

- **FastAPI**: API REST moderna y rápida
- **ChromaDB**: Base de datos vectorial embebida para almacenar metadatos de tablas
- **LangChain**: Framework para RAG y procesamiento de lenguaje natural
- **OpenAI GPT**: LLM GPT-4 para generación de SQL
- **Búsqueda semántica**: Encuentra tablas relevantes basándose en el contexto de la pregunta

## 📋 Requisitos

- Python 3.11+
- OpenAI API Key
- 2GB+ RAM (para ChromaDB y embeddings)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd sql-query-buddy/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear archivo `.env` en el directorio `backend/`:
```env
OPENAI_API_KEY=tu_api_key_de_openai
OPENAI_MODEL=gpt-4
CHROMA_PERSIST_DIRECTORY=./chroma_db
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=*
```

## 🚀 Ejecución

### Desarrollo local
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Con script de inicio
```bash
chmod +x start.sh
./start.sh
```

## 📚 API Endpoints

### `POST /ask`
Genera una consulta SQL basada en una pregunta en lenguaje natural.

**Request:**
```json
{
  "question": "¿Cuántos usuarios se registraron en el último mes?"
}
```

**Response:**
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH);",
  "explanation": "Esta consulta cuenta todos los usuarios...",
  "optimization": "Para mejorar el rendimiento, considera crear un índice en created_at..."
}
```

### `POST /metadata`
Añade metadatos de una tabla a la base vectorial.

**Request:**
```json
{
  "table_name": "users",
  "schema_info": "id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255), created_at TIMESTAMP",
  "description": "Tabla de usuarios del sistema con información básica de registro"
}
```

### `GET /tables`
Obtiene información sobre todas las tablas disponibles.

### `GET /health`
Verifica el estado de salud de la aplicación.

## 🗄️ Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py              # Punto de entrada de FastAPI
│   ├── config.py            # Configuración y variables de entorno
│   └── services/
│       ├── rag.py           # Servicio RAG con ChromaDB
│       └── sql_generator.py # Generación de SQL con LLM
├── requirements.txt          # Dependencias de Python
├── start.sh                 # Script de inicio para Render
└── README.md               # Este archivo
```

## 🔧 Configuración para Render

### Variables de Entorno en Render
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `OPENAI_MODEL`: Modelo de OpenAI a usar (por defecto: gpt-4)
- `PORT`: Puerto (Render lo configura automáticamente)
- `CHROMA_PERSIST_DIRECTORY`: Directorio para persistir ChromaDB

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
./start.sh
```

## 🧪 Testing

### Probar endpoints localmente
```bash
# Health check
curl http://localhost:8000/health

# Generar SQL
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuántos usuarios hay?"}'

# Añadir metadatos
curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{"table_name": "test", "schema_info": "id INT", "description": "Tabla de prueba"}'
```

## 🔍 Debugging

### Logs
La aplicación imprime logs detallados en la consola:
- 🤔 Preguntas recibidas
- ✅ SQL generado exitosamente
- ❌ Errores y excepciones

### ChromaDB
Los datos se almacenan en `./chroma_db/` por defecto. Puedes eliminar este directorio para resetear la base vectorial.

## 🚨 Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"
- Verifica que el archivo `.env` existe y contiene la variable
- En Render, asegúrate de configurar la variable de entorno

### Error: "No se pudo generar la consulta SQL"
- Verifica que tu API key de OpenAI sea válida
- Revisa los logs para más detalles del error

### ChromaDB no persiste datos
- Verifica permisos de escritura en el directorio
- Asegúrate de que `CHROMA_PERSIST_DIRECTORY` esté configurado correctamente

## 📝 Notas de Desarrollo

- El servicio RAG usa embeddings de HuggingFace (`all-MiniLM-L6-v2`)
- Los prompts están optimizados para el modelo GPT-4
- ChromaDB se inicializa automáticamente en el primer uso
- El sistema valida sintácticamente las consultas SQL generadas

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
