FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias de producción
RUN npm ci --only=production

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 3000

# Comando por defecto
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
