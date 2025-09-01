# SQL Query Buddy 🚀

Una aplicación web inteligente que genera consultas SQL usando RAG (Retrieval-Augmented Generation) y LLMs de OpenAI.

## ✨ Características

- **Generación de SQL Inteligente**: Convierte preguntas en lenguaje natural a consultas SQL
- **Sistema RAG**: Utiliza metadatos de tablas para generar SQL más preciso
- **Optimización Automática**: Sugiere mejoras para las consultas generadas
- **Interfaz Web Moderna**: Frontend React con diseño responsive
- **API REST**: Backend FastAPI con documentación automática

## 🏗️ Arquitectura

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4
- **Base Vectorial**: ChromaDB
- **Deployment**: Cloudflare Pages (Frontend) + Render (Backend)

## 🚀 Deployment

### Frontend en Cloudflare Pages
- Automático desde GitHub
- Build command: `npm run build`
- Output directory: `dist`

### Backend en Render
- Tipo de Servicio: **Docker**
- **Root Directory**: `backend`
- **Dockerfile**: `Dockerfile` (o dejar en blanco)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  (Este comando se define en la UI de Render y sobreescribe el `CMD` del Dockerfile)

## 🔧 Configuración Local

### Backend
```bash
cd backend
pip install -r requirements.txt
# Crear archivo .env con OPENAI_API_KEY
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Endpoints

- `GET /` - Información de la API
- `GET /health` - Estado de salud
- `POST /ask` - Generar consulta SQL
- `POST /metadata` - Añadir metadatos de tabla
- `GET /tables` - Listar tablas disponibles

## 🌟 Uso

1. Añade metadatos de tus tablas usando el endpoint `/metadata`
2. Haz preguntas en lenguaje natural
3. Obtén consultas SQL generadas automáticamente
4. Revisa las explicaciones y optimizaciones sugeridas

## 📝 Licencia

MIT License
