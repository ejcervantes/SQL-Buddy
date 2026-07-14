# SQL Query Buddy

SQL Query Buddy es una aplicación full-stack diseñada para traducir preguntas en lenguaje natural a consultas SQL. Utilizando el poder de los Modelos de Lenguaje Grandes (LLM) y la técnica de Generación Aumentada por Recuperación (RAG), esta aplicación no solo genera la consulta SQL, sino que también proporciona una explicación clara de su funcionamiento y una sugerencia de optimización relevante.

El objetivo principal es permitir a los usuarios, tanto técnicos como no técnicos, interactuar con bases de datos de una manera más intuitiva, sin necesidad de escribir SQL manualmente.

## 🔗 Enlaces de Despliegue

La aplicación desplegada simula la base de datos de una tienda por conveniencia. Cuenta con 3 tablas por el momento:
- Clientes: Esta tabla almacena información sobre los clientes de la empresa. Contiene datos personales como nombre y email, la fecha en que se registraron y su país de origen.
- Productos: Esta tabla contiene información de los productos de la tienda, con valores como precio, stock y categoria.
- Ventas: La tabla contiene información de los pedidos de la tienda, con información como el pedido, el producto, la fecha y compra total.

Puedes interactuar con la aplicación desplegada directamente a través de los siguientes enlaces:

<ul>
<li>| Servicio          | Enlace de Despliegue                          |</li>
<li>| **Frontend (UI)** | https://sql-buddy.pages.dev                   |</li>
<li>| **Backend (API)** | https://sql-buddy-backend-g3cu.onrender.com   |</li>
</ul>

## 📝 Descripción

- **Generación de SQL Inteligente**: Convierte preguntas en lenguaje natural a consultas SQL
- **Sistema RAG**: Introspecta el esquema de la base de datos en vivo (vía `information_schema`) y almacena los embeddings en PostgreSQL usando la extensión `pgvector` (en el mismo proyecto de Supabase), de modo que la base vectorial es persistente y gratuita. Al arrancar compara un fingerprint (hash) del esquema y solo re-vectoriza cuando la estructura realmente cambia.
- **Análisis de Consultas**: Ofrece una explicación de la consulta generada y sugiere posibles optimizaciones.
- **Interfaz Web Moderna**: Frontend construido con React y Vite, con un diseño limpio y responsive.
- **API REST**: Backend desarrollado con FastAPI que expone endpoints claros y está documentado.

## 🏗️ Arquitectura

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4
- **Base Vectorial**: PostgreSQL + pgvector (almacenada en Supabase)
- **Base de Datos**: Supabase (PostgreSQL)
- **Despliegue**: Hosting estático (Cloudflare Pages / Hostinger) para el frontend + Render para el backend

## 🚀 Despliegue

La arquitectura de despliegue separa el frontend estático del backend dinámico, cada uno desplegado de forma independiente.

### Frontend (hosting estático)
El frontend de React se compila con Vite y se despliega como sitio estático (ej. Cloudflare Pages o Hostinger). Define las variables de entorno de build: `VITE_API_URL` (la URL del backend), `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY`.

### Backend en Render
El backend de FastAPI está empaquetado en un contenedor Docker (`backend/Dockerfile`) y desplegado en Render. Variables de entorno requeridas: `OPENAI_API_KEY` y `DATABASE_URL` (la cadena de conexión de Supabase; usa la URL del **Session pooler**). Habilita la extensión `vector` en Supabase de antemano. En el primer arranque el backend crea automáticamente las tablas de pgvector y una tabla `rag_schema_meta`, y siembra la base vectorial desde el esquema en vivo.

## 📚 API Endpoints

- `GET /` - Endpoint raíz que devuelve un mensaje de bienvenida. Útil para verificar que la API está en funcionamiento.
- `GET /health` - Proporciona un chequeo de salud del sistema, verificando el estado de servicios críticos como OpenAI y la base vectorial pgvector.
- `POST /ask` - Es el endpoint principal. Recibe una pregunta en lenguaje natural y devuelve la consulta SQL generada.
- `GET /tables` - Devuelve una lista de todas las tablas cuyos metadatos están actualmente cargados en la base vectorial.
- `POST /resync` - Fuerza la re-vectorización del esquema sin reiniciar el servicio. Opcionalmente protegido con el header `X-Resync-Token` (cuando `RESYNC_TOKEN` está configurado).
