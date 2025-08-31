from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from app.config import settings
from app.services.rag import RAGService
from app.services.sql_generator import SQLGeneratorService

# Inicializar FastAPI
app = FastAPI(
    title="SQL Query Buddy (RAG)",
    description="API para generar consultas SQL usando RAG y LLM",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para las requests
class QuestionRequest(BaseModel):
    question: str

class MetadataRequest(BaseModel):
    table_name: str
    schema_info: str
    description: str

class SQLResponse(BaseModel):
    sql: str
    explanation: str
    optimization: str

# Inicializar servicios
rag_service = RAGService()
sql_generator = SQLGeneratorService(rag_service)

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    print("🚀 Iniciando SQL Query Buddy (RAG)...")
    
    # Validar configuración
    if not settings.validate():
        print("⚠️  La aplicación puede no funcionar correctamente debido a configuraciones faltantes")
    
    print(f"✅ Aplicación iniciada en {settings.HOST}:{settings.PORT}")
    print(f"🔑 Modelo LLM: {settings.OPENAI_MODEL}")
    print(f"🗄️  Base vectorial: {settings.CHROMA_PERSIST_DIRECTORY}")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "SQL Query Buddy (RAG) API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "ask": "POST /ask - Generar consulta SQL",
            "metadata": "POST /metadata - Añadir metadatos de tabla",
            "health": "GET /health - Estado de la aplicación"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud de la aplicación"""
    try:
        # Verificar que los servicios estén funcionando
        test_response = rag_service.query_openai("Responde solo 'OK' si estás funcionando.")
        
        return {
            "status": "healthy",
            "services": {
                "rag_service": "operational",
                "sql_generator": "operational",
                "llm": "operational" if "OK" in test_response else "error"
            },
            "config": {
                "model": settings.OPENAI_MODEL,
                "chroma_directory": settings.CHROMA_PERSIST_DIRECTORY
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en health check: {str(e)}"
        )

@app.post("/ask", response_model=SQLResponse)
async def ask_question(request: QuestionRequest):
    """
    Genera una consulta SQL basada en una pregunta en lenguaje natural
    
    Args:
        request: Pregunta del usuario
        
    Returns:
        Consulta SQL generada con explicación y optimización
    """
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="La pregunta no puede estar vacía"
            )
        
        print(f"🤔 Pregunta recibida: {request.question}")
        
        # Generar SQL usando el servicio
        result = sql_generator.generate_sql_query(request.question)
        
        print(f"✅ SQL generado exitosamente")
        
        return SQLResponse(
            sql=result["sql"],
            explanation=result["explanation"],
            optimization=result["optimization"]
        )
        
    except Exception as e:
        print(f"❌ Error generando SQL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.post("/metadata")
async def add_table_metadata(request: MetadataRequest):
    """
    Añade o actualiza metadatos de una tabla en la base vectorial
    
    Args:
        request: Metadatos de la tabla
        
    Returns:
        Confirmación de la operación
    """
    try:
        if not all([request.table_name.strip(), request.schema_info.strip()]):
            raise HTTPException(
                status_code=400,
                detail="El nombre de la tabla y la información del esquema son obligatorios"
            )
        
        print(f"📝 Añadiendo metadatos para tabla: {request.table_name}")
        
        # Añadir metadatos usando el servicio RAG
        success = rag_service.add_table_metadata(
            table_name=request.table_name,
            schema_info=request.schema_info,
            description=request.description
        )
        
        if success:
            print(f"✅ Metadatos añadidos exitosamente para: {request.table_name}")
            return {
                "message": f"Metadatos de la tabla '{request.table_name}' añadidos exitosamente",
                "table_name": request.table_name,
                "status": "success"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudieron añadir los metadatos para la tabla '{request.table_name}'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error añadiendo metadatos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/tables")
async def get_tables():
    """
    Obtiene información sobre todas las tablas disponibles en la base vectorial
    
    Returns:
        Lista de tablas con sus metadatos
    """
    try:
        # Buscar todas las tablas (búsqueda genérica)
        results = rag_service.search_relevant_tables("", top_k=50)
        
        # Filtrar solo tablas únicas
        unique_tables = {}
        for result in results:
            table_name = result["metadata"].get("table_name", "Unknown")
            if table_name not in unique_tables:
                unique_tables[table_name] = {
                    "table_name": table_name,
                    "description": result["content"],
                    "metadata": result["metadata"]
                }
        
        return {
            "tables": list(unique_tables.values()),
            "total_count": len(unique_tables)
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo tablas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

if __name__ == "__main__":
    # Ejecutar con uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Solo para desarrollo
    )
