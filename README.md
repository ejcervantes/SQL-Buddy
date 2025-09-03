# SQL Query Buddy

SQL Query Buddy is a full-stack application designed to translate natural language questions into SQL queries. Using the power of Large Language Models (LLM) and the Retrieval-Augmented Generation (RAG) technique, this application not only generates the SQL query but also provides a clear explanation of its functionality and a relevant optimization suggestion.

The main objective is to allow users, both technical and non-technical, to interact with databases in a more intuitive way, without the need to write SQL manually.

## 🔗 Deployment Links

You can interact with the deployed application directly through the following links:

| Servicio          | Enlace de Despliegue                          |  
| **Frontend (UI)** | https://sql-buddy.pages.dev                   |  
| **Backend (API)** | https://sql-buddy-backend-g3cu.onrender.com   |  

## 📝 Description

- **Intelligent SQL Generation**: Converts natural language questions into SQL queries.
- **RAG System**: Uses a JSON file to load table schemas into a vector database, providing precise context to the LLM.
- **Question Analysis**: Offers an explanation of the generated query and suggests possible optimizations.
- **Modern Web Interface**: Frontend built with React and Vite, with a clean and responsive design.
- **REST API**: Backend developed with FastAPI that exposes clear and documented endpoints.

## 🏗️ Arquitecture

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4
- **Vector Database**: ChromaDB
- **Deployment**: Cloudflare Pages (Frontend) + Render (Backend)

## 🚀 Deployment

The deployment architecture is designed to optimize performance and facilitate management by separating the static frontend from the dynamic backend.

### Frontend on Cloudflare Pages
The React frontend is deployed on Cloudflare Pages. This service is optimized for serving static sites at high speed through its global content delivery network (CDN). It integrates directly with the GitHub repository, automatically deploying each new change on the main branch.

### Backend on Render
The FastAPI backend is packaged in a Docker container and deployed on Render. This platform is ideal for containerized web services, automatically managing scaling, SSL certificates, and environment variables. The service is configured to run from the backend/ directory of the repository.

## 📚 API Endpoints

- `GET /` - Root endpoint that returns a welcome message. Useful for verifying that the API is running.
- `GET /health` - Provides a system health check, verifying the status of critical services like the connection to the vector database.
- `POST /ask` - This is the main endpoint. It receives a question in natural language and returns the generated SQL query.
- `GET /tables` - Returns a list of all tables whose metadata is currently loaded into the vector database.
