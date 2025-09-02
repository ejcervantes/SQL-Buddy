import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.services.rag_chroma import RAGServiceChroma
from app.services.sql_generator import SQLGeneratorService

# --- Modelos de Datos (Pydantic) ---

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    sql_query: str
    explanation: str
    optimization: str

class MetadataRequest(BaseModel):
    table_name: str
    schema_info: str
    description: str

class HealthCheckResponse(BaseModel):
    status: str
    services: dict

# --- Inicialización de la Aplicación ---

app = FastAPI(
    title="SQL Query Buddy API",
    description="API para generar consultas SQL usando RAG y LLMs.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inicialización de Servicios ---

rag_service = RAGServiceChroma()
sql_generator = SQLGeneratorService(rag_service)

# --- Eventos de Ciclo de Vida ---

@app.on_event("startup")
async def load_seed_metadata():
    print("🚀 Aplicación iniciada. Cargando metadatos iniciales...")
    try:
        current_dir = os.path.dirname(__file__)
        seed_file_path = os.path.join(current_dir, "metadata_seed.json")

        if not os.path.exists(seed_file_path):
            print("⚠️  Advertencia: No se encontró 'metadata_seed.json'. No se cargarán metadatos iniciales.")
            return

        with open(seed_file_path, "r", encoding="utf-8") as f:
            seed_data = json.load(f)
            
        tables_loaded = 0
        existing_tables = rag_service.get_available_tables()
        print(f"ℹ️  Tablas existentes en la base vectorial: {existing_tables}")

        for table_meta in seed_data:
            if table_meta["table_name"] not in existing_tables:
                success = rag_service.add_table_metadata(
                    table_name=table_meta["table_name"],
                    schema_info=table_meta["schema_info"],
                    description=table_meta["description"]
                )
                if success:
                    tables_loaded += 1
        
        if tables_loaded > 0:
            print(f"✅ Se sembraron exitosamente los metadatos de {tables_loaded} nuevas tablas.")
        else:
            print("ℹ️  No se sembraron nuevas tablas (todas las tablas del seed ya existían).")

    except Exception as e:
        print(f"❌ Error crítico al cargar metadatos iniciales: {e}")

# --- Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido a SQL Query Buddy API"}

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return {
        "status": "ok",
        "services": {
            "openai_embeddings": rag_service.query_openai("health check"),
            "vector_db": "connected" if rag_service.vector_store else "disconnected"
        }
    }

@app.get("/tables")
def get_tables():
    try:
        table_names = rag_service.get_available_tables()
        return {
            "tables": [{"name": name} for name in table_names],
            "count": len(table_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tablas: {e}")

@app.post("/ask", response_model=AskResponse, tags=["SQL Generation"])
async def ask_question(request: AskRequest) -> AskResponse:
    try:
        print(f"🚀 Recibida pregunta para generar SQL: '{request.question}'")
        result = sql_generator.generate_sql_query(request.question)
        
        return AskResponse(
            sql_query=result["sql"],
            explanation=result["explanation"],
            optimization=result["optimization"]
        )
    except Exception as e:
        print(f"❌ Error generando SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al generar la consulta SQL: {e}")