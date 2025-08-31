# SQL Query Buddy (RAG) - Frontend

Frontend de React para SQL Query Buddy (RAG), una aplicación que genera consultas SQL usando inteligencia artificial.

## 🚀 Características

- **React 18**: Framework moderno para la interfaz de usuario
- **Vite**: Herramienta de build rápida y moderna
- **Diseño Responsive**: Funciona perfectamente en dispositivos móviles y desktop
- **Interfaz Intuitiva**: Formulario simple para hacer preguntas en lenguaje natural
- **Resultados Organizados**: Muestra SQL, explicación y optimización en pestañas
- **Estado de API**: Indicador visual del estado de conexión con el backend
- **Ejemplos Integrados**: Botones con ejemplos de preguntas comunes

## 📋 Requisitos

- Node.js 16+ 
- npm o yarn
- Backend de SQL Query Buddy funcionando

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd sql-query-buddy/frontend
```

### 2. Instalar dependencias
```bash
npm install
# o
yarn install
```

### 3. Configurar variables de entorno
Crear archivo `.env` en el directorio `frontend/`:
```env
# URL del backend (cambiar según el entorno)
VITE_API_URL=http://localhost:8000

# Para producción, usar la URL de Render:
# VITE_API_URL=https://sqlbuddy.onrender.com
```

### 4. Ejecutar en desarrollo
```bash
npm run dev
# o
yarn dev
```

La aplicación se abrirá en `http://localhost:3000`

## 🏗️ Build para Producción

### Build local
```bash
npm run build
# o
yarn build
```

### Preview del build
```bash
npm run preview
# o
yarn preview
```

## 🌐 Despliegue en Cloudflare Pages

### 1. Conectar repositorio
- Ve a [Cloudflare Pages](https://pages.cloudflare.com/)
- Conecta tu repositorio de GitHub/GitLab
- Selecciona la rama principal

### 2. Configurar build
- **Framework preset**: None
- **Build command**: `npm run build`
- **Build output directory**: `dist`
- **Root directory**: `frontend`

### 3. Variables de entorno
Configura en la sección "Environment variables":
```
VITE_API_URL=https://tu-backend.onrender.com
```

### 4. Desplegar
- Haz push a tu rama principal
- Cloudflare Pages construirá y desplegará automáticamente

## 🗄️ Estructura del Proyecto

```
frontend/
├── public/                 # Archivos estáticos
├── src/
│   ├── components/         # Componentes React
│   │   ├── QueryForm.jsx   # Formulario de consulta
│   │   ├── QueryForm.css   # Estilos del formulario
│   │   ├── ResultCard.jsx  # Tarjeta de resultados
│   │   └── ResultCard.css  # Estilos de resultados
│   ├── App.jsx             # Componente principal
│   ├── App.css             # Estilos principales
│   ├── api.js              # Cliente de API
│   ├── main.jsx            # Punto de entrada
│   └── index.css           # Estilos base
├── index.html              # HTML principal
├── package.json            # Dependencias y scripts
├── vite.config.js          # Configuración de Vite
└── README.md              # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `VITE_API_URL` | URL del backend | `http://localhost:8000` |

### Personalización

#### Colores
Los colores se pueden personalizar editando las variables CSS en `src/index.css`:
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --accent-color: #f093fb;
  /* ... más variables */
}
```

#### Estilos
Cada componente tiene su propio archivo CSS que se puede modificar:
- `QueryForm.css` - Estilos del formulario
- `ResultCard.css` - Estilos de los resultados
- `App.css` - Estilos de la aplicación principal

## 📱 Características de UX

### Formulario Inteligente
- Validación en tiempo real
- Contador de caracteres
- Ejemplos de preguntas integrados
- Botón de envío con estado de carga

### Resultados Organizados
- Pestañas para SQL, explicación y optimización
- Botón de copiar SQL al portapapeles
- Enlaces a herramientas externas (formateador, probador)
- Metadatos del resultado

### Estado de la Aplicación
- Banner de estado de la API
- Indicadores de carga
- Manejo de errores con reintentos
- Mensajes informativos

## 🔌 Integración con Backend

### Endpoints Utilizados
- `POST /ask` - Generar consulta SQL
- `GET /health` - Verificar estado de la API
- `GET /` - Información de la API

### Manejo de Errores
- Timeout de 30 segundos para requests
- Reintentos automáticos en caso de fallo
- Mensajes de error descriptivos
- Fallback graceful en caso de desconexión

## 🧪 Testing

### Ejecutar tests
```bash
npm run test
# o
yarn test
```

### Ejecutar linting
```bash
npm run lint
# o
yarn lint
```

## 📊 Rendimiento

### Optimizaciones Implementadas
- **Code Splitting**: Separación de vendor chunks
- **Lazy Loading**: Componentes cargados bajo demanda
- **CSS Variables**: Reutilización de estilos
- **Animaciones CSS**: Transiciones suaves y eficientes
- **Responsive Images**: Optimización para diferentes dispositivos

### Métricas de Rendimiento
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## 🚨 Solución de Problemas

### Error: "No se pudo conectar con el servidor"
- Verifica que el backend esté funcionando
- Confirma la URL en `VITE_API_URL`
- Revisa la consola del navegador para errores CORS

### Error: "Module not found"
- Ejecuta `npm install` para reinstalar dependencias
- Verifica que estés en el directorio correcto
- Limpia la caché: `npm run clean`

### Problemas de Build
- Verifica que Node.js sea versión 16+
- Limpia node_modules: `rm -rf node_modules && npm install`
- Verifica la configuración de Vite

## 🔒 Seguridad

### Consideraciones
- No se almacenan datos sensibles en el frontend
- Las API keys se manejan solo en el backend
- Validación de entrada en el cliente
- Sanitización de datos antes de renderizar

### Headers de Seguridad
- CORS configurado apropiadamente
- CSP headers recomendados para producción
- HTTPS obligatorio en producción

## 📈 Monitoreo

### Logs del Cliente
- Errores de API se registran en consola
- Métricas de rendimiento disponibles
- Estado de conexión visible al usuario

### Métricas Recomendadas
- Tiempo de respuesta de la API
- Tasa de éxito de generación de SQL
- Uso de características por dispositivo
- Errores de usuario comunes

## 🤝 Contribución

### Desarrollo Local
1. Fork el proyecto
2. Crea una rama para tu feature
3. Instala dependencias: `npm install`
4. Ejecuta en desarrollo: `npm run dev`
5. Haz commit de tus cambios
6. Abre un Pull Request

### Estándares de Código
- Usar ESLint y Prettier
- Seguir convenciones de React
- Documentar funciones complejas
- Mantener componentes pequeños y reutilizables

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

### Recursos Útiles
- [Documentación de React](https://reactjs.org/docs/)
- [Documentación de Vite](https://vitejs.dev/)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)

### Comunidad
- Issues en GitHub
- Discusiones en el repositorio
- Documentación del proyecto

---

**SQL Query Buddy (RAG)** - Transformando preguntas en consultas SQL con IA 🚀
