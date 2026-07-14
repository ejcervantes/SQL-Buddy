"""
Servicio RAG respaldado por pgvector en Postgres (Supabase).

Los embeddings del esquema se almacenan en la MISMA base de datos de Supabase
mediante la extensión `pgvector`. Así la base vectorial es persistente y gratuita,
y el backend puede ser sin estado (ideal para Render free, que no tiene disco).

Además, guarda un "fingerprint" (hash) del esquema en la tabla `rag_schema_meta`.
Al arrancar, la app compara el fingerprint actual con el guardado y solo re-vectoriza
cuando el esquema cambió (ahorra llamadas de embeddings y tiempo de arranque).
"""

import json

import psycopg2
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.pgvector import PGVector

from app.config import settings

# Nombre de la colección de vectores dentro de pgvector.
COLLECTION_NAME = "sql_buddy_schema"


def _to_sqlalchemy_url(database_url: str) -> str:
    """PGVector usa SQLAlchemy, que requiere el driver explícito psycopg2."""
    for prefix in ("postgresql://", "postgres://"):
        if database_url.startswith(prefix):
            return "postgresql+psycopg2://" + database_url[len(prefix):]
    return database_url


class RAGServicePGVector:
    """Gestiona la base vectorial (pgvector) y el fingerprint del esquema."""

    def __init__(self):
        if not settings.validate():
            raise ValueError("Configuración inválida. Revisa las variables de entorno.")
        if not settings.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL es obligatoria: la base vectorial se guarda en Postgres/pgvector."
            )

        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100, length_function=len
        )
        self.connection_string = _to_sqlalchemy_url(settings.DATABASE_URL)

        # Apunta a la colección existente (la crea si aún no existe).
        self.vector_store = PGVector(
            connection_string=self.connection_string,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME,
        )
        self._ensure_meta_table()
        print("✅ Servicio RAG con pgvector inicializado.")

    # ---------------------------------------------------------------
    # Metadatos / fingerprint (tabla rag_schema_meta)
    # ---------------------------------------------------------------
    def _ensure_meta_table(self):
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rag_schema_meta (
                        id integer PRIMARY KEY DEFAULT 1,
                        fingerprint text,
                        tables jsonb,
                        updated_at timestamptz DEFAULT now(),
                        CONSTRAINT rag_schema_meta_single_row CHECK (id = 1)
                    )
                    """
                )
            conn.commit()
        finally:
            conn.close()

    def get_stored_fingerprint(self) -> str | None:
        """Devuelve el fingerprint del esquema con el que se construyó la base vectorial."""
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT fingerprint FROM rag_schema_meta WHERE id = 1")
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"⚠️  No se pudo leer el fingerprint: {e}")
            return None
        finally:
            conn.close()

    def _save_meta(self, fingerprint: str, tables: list[str]):
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rag_schema_meta (id, fingerprint, tables, updated_at)
                    VALUES (1, %s, %s, now())
                    ON CONFLICT (id) DO UPDATE
                    SET fingerprint = EXCLUDED.fingerprint,
                        tables = EXCLUDED.tables,
                        updated_at = now()
                    """,
                    (fingerprint, json.dumps(tables)),
                )
            conn.commit()
        finally:
            conn.close()

    def get_available_tables(self) -> list[str]:
        """Lista las tablas actualmente cargadas en la base vectorial."""
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT tables FROM rag_schema_meta WHERE id = 1")
                row = cur.fetchone()
                if row and row[0]:
                    return sorted(row[0])
                return []
        except Exception as e:
            print(f"❌ Error obteniendo la lista de tablas: {e}")
            return []
        finally:
            conn.close()

    def has_vectors(self) -> bool:
        return bool(self.get_available_tables())

    # ---------------------------------------------------------------
    # Reconstrucción de la base vectorial
    # ---------------------------------------------------------------
    def rebuild(self, metadata: list[dict], fingerprint: str):
        """Re-vectoriza todo el esquema y reemplaza la colección existente."""
        documents = []
        table_names = []
        for table in metadata:
            table_names.append(table["table_name"])
            content = (
                f"Tabla: {table['table_name']}\n"
                f"Esquema: {table['schema_info']}\n"
                f"Descripción: {table['description']}"
            )
            documents.extend(
                self.text_splitter.create_documents(
                    [content],
                    metadatas=[{"table_name": table["table_name"], "source": "metadata"}],
                )
            )

        # pre_delete_collection=True limpia la colección antes de insertar los nuevos vectores.
        self.vector_store = PGVector.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=COLLECTION_NAME,
            connection_string=self.connection_string,
            pre_delete_collection=True,
        )
        self._save_meta(fingerprint, table_names)
        print(
            f"✅ Base vectorial reconstruida en pgvector "
            f"({len(table_names)} tablas, {len(documents)} fragmentos)."
        )

    # ---------------------------------------------------------------
    # Búsqueda / contexto para el LLM
    # ---------------------------------------------------------------
    def search_relevant_tables(self, query: str, top_k: int = 5) -> list:
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            return [
                {"content": doc.page_content, "metadata": doc.metadata, "score": float(score)}
                for doc, score in results
            ]
        except Exception as e:
            print(f"❌ Error durante la búsqueda de similitud: {e}")
            return []

    def get_context_for_sql_generation(self, query: str, top_k: int = 3) -> str:
        print(f"🔎 Buscando contexto para la pregunta: '{query}'")
        relevant_tables = self.search_relevant_tables(query, top_k=top_k)
        if not relevant_tables:
            print("⚠️ No se encontraron tablas relevantes para la pregunta.")
            return "No se encontraron metadatos de tablas relevantes."

        context = "Aquí están los esquemas de las tablas relevantes para la pregunta:\n\n"
        for table in relevant_tables:
            context += f"---\n{table['content']}\n---\n"
        return context

    def query_openai(self, text: str) -> str:
        """Prueba de conexión con OpenAI para el health check."""
        try:
            self.embeddings.embed_query(text)
            return "OK"
        except Exception as e:
            print(f"Error en query_openai (health check): {e}")
            return f"Error: {e}"
