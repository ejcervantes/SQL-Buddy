import os
import json
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.services.rag_service import RAGServicePGVector
from app.services.sql_generator import SQLGeneratorService
from app.services.schema_introspector import fetch_schema_metadata, compute_schema_fingerprint

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

rag_service = RAGServicePGVector()
sql_generator = SQLGeneratorService(rag_service)

# --- Eventos de Ciclo de Vida ---

def _load_metadata_from_db() -> list | None:
    """Intenta leer el esquema en vivo desde Postgres. Devuelve None si no aplica."""
    if not settings.DATABASE_URL:
        print("ℹ️  DATABASE_URL no configurada. Se usará metadata_seed.json como respaldo.")
        return None
    try:
        metadata = fetch_schema_metadata()
        print(f"✅ Esquema leído en vivo desde la base de datos ({len(metadata)} tablas).")
        return metadata
    except Exception as e:
        print(f"⚠️  No se pudo leer el esquema desde la base de datos ({e}). "
              f"Se usará metadata_seed.json como respaldo.")
        return None


def _load_metadata_from_json() -> list:
    """Respaldo: lee los metadatos desde metadata_seed.json."""
    current_dir = os.path.dirname(__file__)
    seed_file_path = os.path.join(current_dir, "metadata_seed.json")

    if not os.path.exists(seed_file_path):
        print("⚠️  Advertencia: No se encontró 'metadata_seed.json'. No se cargarán metadatos iniciales.")
        return []

    with open(seed_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_vector_sync(force: bool = False) -> dict:
    """
    Sincroniza la base vectorial (pgvector en Supabase) con el esquema actual.

    Solo re-vectoriza si el esquema cambió (comparando el fingerprint), si aún no
    existe base vectorial, o si se fuerza (force=True). En el caso normal (esquema
    sin cambios) reutiliza los vectores persistidos en Supabase.

    Devuelve un resumen de lo que ocurrió (útil para logs y para /resync).
    """
    # Fuente de verdad preferida: el esquema real de la base de datos.
    # Si no hay conexión disponible, se recurre al JSON de respaldo.
    seed_data = _load_metadata_from_db()
    if seed_data is None:
        seed_data = _load_metadata_from_json()

    if not seed_data:
        print("⚠️  Sin metadatos para vectorizar.")
        return {"status": "no_metadata", "rebuilt": False, "tables": []}

    fingerprint = compute_schema_fingerprint(seed_data)
    stored_fingerprint = rag_service.get_stored_fingerprint()
    up_to_date = stored_fingerprint == fingerprint and rag_service.has_vectors()

    if up_to_date and not force:
        print("✅ La base vectorial ya está al día (el esquema no cambió). No se re-vectoriza.")
        return {"status": "up_to_date", "rebuilt": False, "tables": rag_service.get_available_tables()}

    if force:
        reason = "resync forzado"
    elif not rag_service.has_vectors():
        reason = "no existe base vectorial"
    else:
        reason = "el esquema cambió"

    print(f"🔁 Reconstruyendo la base vectorial ({reason})...")
    rag_service.rebuild(seed_data, fingerprint)
    return {"status": "rebuilt", "reason": reason, "rebuilt": True, "tables": rag_service.get_available_tables()}


@app.on_event("startup")
async def sync_vector_store():
    print("🚀 Aplicación iniciada. Sincronizando la base vectorial...")
    try:
        result = run_vector_sync(force=False)
        print(f"ℹ️  Sincronización: {result['status']} ({len(result['tables'])} tablas).")
    except Exception as e:
        print(f"❌ Error crítico al sincronizar la base vectorial: {e}")

# --- Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido a SQL Query Buddy API"}

@app.post("/resync", tags=["RAG"])
def resync_vector_store(x_resync_token: str | None = Header(default=None)):
    """
    Fuerza la re-vectorización del esquema sin reiniciar el servicio.

    Si RESYNC_TOKEN está configurado, exige el header 'X-Resync-Token' con ese valor
    (evita que cualquiera dispare re-embeddings). Si no está configurado, queda abierto.
    """
    if settings.RESYNC_TOKEN and x_resync_token != settings.RESYNC_TOKEN:
        raise HTTPException(status_code=401, detail="Token de resync inválido o ausente.")
    try:
        return run_vector_sync(force=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al re-sincronizar la base vectorial: {e}")

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