# SQL Query Buddy

SQL Query Buddy is a full-stack application designed to translate natural language questions into SQL queries. Using the power of Large Language Models (LLM) and the Retrieval-Augmented Generation (RAG) technique, this application not only generates the SQL query but also provides a clear explanation of its functionality and a relevant optimization suggestion.

The main objective is to allow users, both technical and non-technical, to interact with databases in a more intuitive way, without the need to write SQL manually.

## 🔗 Deployment Links

The deployed application simulates the database of a convenience store. It currently has three tables:
- Customers: This table stores information about the company's customers. It contains personal data such as name and email address, registration date, and country of origin.
- Products: This table contains information about the store's products, with values ​​such as price, stock, and category.
- Sales: This table contains information about the store's orders, with information such as the order, product, date, and total purchase.

It was developed in Spanish, but it can work with English questions too. For a better experience, I recommend not using the Google Translate feature, as it tends to interfere with the application when testing the query.

You can interact with the deployed application directly through the following links:

| Servicio          | Enlace de Despliegue                          |  
| **Frontend (UI)** | https://sql-buddy.pages.dev                   |  
| **Backend (API)** | https://sql-buddy-backend-g3cu.onrender.com   |  

## 📝 Description

- **Intelligent SQL Generation**: Converts natural language questions into SQL queries.
- **RAG System**: Introspects the database schema live (via `information_schema`) and stores the embeddings in PostgreSQL using the `pgvector` extension (in the same Supabase project), so the vector store is persistent and free. On startup it compares a fingerprint (hash) of the schema and only re-vectorizes when the structure actually changes.
- **Question Analysis**: Offers an explanation of the generated query and suggests possible optimizations.
- **Modern Web Interface**: Frontend built with React and Vite, with a clean and responsive design.
- **REST API**: Backend developed with FastAPI that exposes clear and documented endpoints.

## 🏗️ Arquitecture

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4
- **Vector Store**: PostgreSQL + pgvector (stored in Supabase)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Static hosting (Cloudflare Pages / Hostinger) for the frontend + Render for the backend

## 🚀 Deployment

The deployment architecture separates the static frontend from the dynamic backend, each deployed independently.

### Frontend (static hosting)
The React frontend is built with Vite and deployed as a static site (e.g., Cloudflare Pages or Hostinger). Set the build-time environment variables: `VITE_API_URL` (the backend URL), `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`.

### Backend on Render
The FastAPI backend is packaged in a Docker container (`backend/Dockerfile`) and deployed on Render. Required environment variables: `OPENAI_API_KEY` and `DATABASE_URL` (the Supabase connection string; use the **Session pooler** URL). Enable the `vector` extension in Supabase beforehand. On first run the backend creates the pgvector tables and a small `rag_schema_meta` table automatically, and seeds the vector store from the live schema.

## 📚 API Endpoints

- `GET /` - Root endpoint that returns a welcome message. Useful for verifying that the API is running.
- `GET /health` - Provides a system health check, verifying the status of critical services like OpenAI and the pgvector store.
- `POST /ask` - This is the main endpoint. It receives a question in natural language and returns the generated SQL query.
- `GET /tables` - Returns a list of all tables whose metadata is currently loaded into the vector store.
- `POST /resync` - Forces re-vectorization of the schema without restarting the service. Optionally protected by the `X-Resync-Token` header (when `RESYNC_TOKEN` is set).
