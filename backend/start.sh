#!/bin/bash

echo "🚀 Iniciando SQL Query Buddy (RAG) Backend..."

# Verificar variables de entorno
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  ADVERTENCIA: OPENAI_API_KEY no está configurada"
fi

if [ -z "$PORT" ]; then
    echo "ℹ️  PORT no configurado, usando puerto por defecto 8000"
    export PORT=8000
fi

# Establecer el directorio de persistencia de ChromaDB si no está configurado
CHROMA_PERSIST_DIRECTORY=${CHROMA_PERSIST_DIRECTORY:-./chroma_db}

# Crear directorio para ChromaDB si no existe
echo "🔧 Asegurando que el directorio de ChromaDB exista en: $CHROMA_PERSIST_DIRECTORY"
mkdir -p "$CHROMA_PERSIST_DIRECTORY"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Iniciar la aplicación con uvicorn
echo "🌐 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
