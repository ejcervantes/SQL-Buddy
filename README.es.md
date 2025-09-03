# SQL Query Buddy

SQL Query Buddy es una aplicación full-stack diseñada para traducir preguntas en lenguaje natural a consultas SQL. Utilizando el poder de los Modelos de Lenguaje Grandes (LLM) y la técnica de Generación Aumentada por Recuperación (RAG), esta aplicación no solo genera la consulta SQL, sino que también proporciona una explicación clara de su funcionamiento y una sugerencia de optimización relevante.

El objetivo principal es permitir a los usuarios, tanto técnicos como no técnicos, interactuar con bases de datos de una manera más intuitiva, sin necesidad de escribir SQL manualmente.

## 🔗 Enlaces de Despliegue

Puedes interactuar con la aplicación desplegada directamente a través de los siguientes enlaces:
<ul>
<li>| Servicio          | Enlace de Despliegue                          |</li>
<li>| **Frontend (UI)** | https://sql-buddy.pages.dev                   |</li>
<li>| **Backend (API)** | https://sql-buddy-backend-g3cu.onrender.com   |</li>
</ul>

## 📝 Descripción

- **Generación de SQL Inteligente**: Convierte preguntas en lenguaje natural a consultas SQL
- **Sistema RAG**: Utiliza un archivo JSON para cargar los esquemas de las tablas en una base de datos vectorial, proporcionando un contexto preciso al LLM.
- **Análisis de Consultas**: Ofrece una explicación de la consulta generada y sugiere posibles optimizaciones.
- **Interfaz Web Moderna**: Frontend construido con React y Vite, con un diseño limpio y responsive.
- **API REST**: Backend desarrollado con FastAPI que expone endpoints claros y está documentado.

## 🏗️ Arquitectura

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4
- **Base Vectorial**: ChromaDB
- **Despliegue**: Cloudflare Pages (Frontend) + Render (Backend)

## 🚀 Despliegue

La arquitectura de despliegue está diseñada para optimizar el rendimiento y facilitar la gestión, separando el frontend estático del backend dinámico.

### Frontend en Cloudflare Pages
El frontend de React se despliega en Cloudflare Pages. Este servicio está optimizado para servir sitios estáticos a alta velocidad a través de su red de distribución de contenido (CDN) global. Se integra directamente con el repositorio de GitHub, desplegando automáticamente cada nuevo cambio en la rama principal.

### Backend en Render
El backend de FastAPI está empaquetado en un contenedor Docker y desplegado en Render. Esta plataforma es ideal para servicios web en contenedores, gestionando automáticamente el escalado, los certificados SSL y las variables de entorno. El servicio se configura para ejecutarse desde el directorio backend/ del repositorio.

## 📚 API Endpoints

- `GET /` - Endpoint raíz que devuelve un mensaje de bienvenida. Útil para verificar que la API está en funcionamiento.
- `GET /health` - Proporciona un chequeo de salud del sistema, verificando el estado de servicios críticos como la conexión con la base de datos vectorial.
- `POST /ask` - Es el endpoint principal. Recibe una pregunta en lenguaje natural y devuelve la consulta SQL generada.
- `GET /tables` - Devuelve una lista de todas las tablas cuyos metadatos están actualmente cargados en la base de datos vectorial.
