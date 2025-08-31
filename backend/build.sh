#!/bin/bash
set -e

echo "🚀 Iniciando build del backend..."

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del sistema necesarias
apt-get update -qq
apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python con flags específicos
echo "📦 Instalando dependencias de Python..."
pip install --no-cache-dir --only-binary=all -r requirements.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import chromadb; print('ChromaDB instalado correctamente')"
python -c "import fastapi; print('FastAPI instalado correctamente')"

echo "🎉 Build completado exitosamente!"
