# ============================================================
# Imagen única: construye el frontend y lo sirve desde el backend.
# Contexto de build = raíz del repo (necesita frontend/ y backend/).
# ============================================================

# ---------- Etapa 1: build del frontend (React + Vite) ----------
FROM node:20-slim AS frontend-build

WORKDIR /frontend

# Instalar dependencias primero (mejor cache)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copiar el código y construir
COPY frontend/ ./

# Configuración pública que se "hornea" en el bundle en tiempo de build.
# VITE_API_URL se deja vacío: el frontend usa el mismo origen (rutas relativas).
# Las llaves de Supabase son públicas (anon), pero se pasan como build args.
ARG VITE_API_URL=""
ARG VITE_SUPABASE_URL=""
ARG VITE_SUPABASE_ANON_KEY=""
ENV VITE_API_URL=$VITE_API_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

RUN npm run build


# ---------- Etapa 2: backend (FastAPI) + estáticos ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de Python
COPY backend/requirements-modern.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-modern.txt

# Código del backend
COPY backend/ .

# Build del frontend -> carpeta 'static' que sirve FastAPI
COPY --from=frontend-build /frontend/dist ./static

# Usuario sin privilegios
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Render define $PORT en tiempo de ejecución; por defecto 8000 en local.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
