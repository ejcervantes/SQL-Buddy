# Etapa 1: Usar una imagen base de Python moderna y ligera
FROM python:3.11-slim as base

# Evitar que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Asegurar que la salida de Python no se almacene en búfer
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Etapa 2: Instalar dependencias de Python
# Copiar solo el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 3: Configurar el entorno de la aplicación
# Crear un usuario sin privilegios para ejecutar la aplicación
RUN useradd --create-home --shell /bin/bash appuser

# Copiar el código de la aplicación
COPY . .

# Cambiar la propiedad de los archivos al nuevo usuario
RUN chown -R appuser:appuser /app

# Cambiar al usuario sin privilegios
USER appuser

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# El comando para iniciar la aplicación. Render usará el "Start Command" de la UI.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
