#!/bin/bash
set -e

echo "🚀 Iniciando build del backend..."

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip install --no-cache-dir -r requirements.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import chromadb; print('ChromaDB instalado correctamente')"
python -c "import fastapi; print('FastAPI instalado correctamente')"

echo "🎉 Build completado exitosamente!"
