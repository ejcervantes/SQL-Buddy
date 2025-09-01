#!/bin/bash
set -e

echo "🚀 Iniciando SQL Query Buddy (RAG) Backend..."

# Render proporciona la variable PORT. Si no está, se usa 8000 por defecto.
if [ -z "$PORT" ]; then
    echo "ℹ️  PORT no configurado, usando puerto por defecto 8000"
    export PORT=8000
fi

# Iniciar la aplicación con uvicorn
echo "🌐 Iniciando servidor FastAPI en el puerto $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
