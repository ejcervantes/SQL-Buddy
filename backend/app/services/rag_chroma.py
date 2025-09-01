import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.config import settings

class RAGServiceChroma:
    """
    Servicio para gestionar la base de datos vectorial con ChromaDB (persistente).
    """
    def __init__(self):
        """
        Inicializa el servicio RAG, el modelo de embeddings y el cliente de ChromaDB.
        """
        if not settings.validate():
            raise ValueError("Configuración inválida. Revisa las variables de entorno.")

        # 1. Inicializar el modelo de embeddings de OpenAI
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 2. Inicializar el cliente de ChromaDB para almacenamiento persistente
        # El directorio se toma de la configuración
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )

        # 3. Inicializar el divisor de texto
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        print(f"✅ Servicio RAG con ChromaDB inicializado. Directorio: {settings.CHROMA_PERSIST_DIRECTORY}")

    def add_table_metadata(self, table_name: str, schema_info: str, description: str) -> bool:
        """
        Añade metadatos de una tabla a la base vectorial persistente.
        """
        try:
            # Combinar la información en un solo documento de texto
            content = f"Tabla: {table_name}\nEsquema: {schema_info}\nDescripción: {description}"
            
            # Dividir el texto en fragmentos (chunks)
            documents = self.text_splitter.create_documents(
                [content], 
                metadatas=[{"table_name": table_name, "source": "metadata"}]
            )
            
            # Añadir los documentos al vector store (se guardarán en disco)
            self.vector_store.add_documents(documents)
            
            print(f"✅ Metadatos de tabla '{table_name}' añadidos a ChromaDB.")
            return True
        except Exception as e:
            print(f"❌ Error al añadir metadatos para '{table_name}': {e}")
            return False

    def search_relevant_tables(self, query: str, top_k: int = 5) -> list:
        """
        Busca en la base vectorial los metadatos de tablas más relevantes para una consulta.
        """
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            # Formatear los resultados para que sean más fáciles de usar
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            return formatted_results
        except Exception as e:
            print(f"❌ Error durante la búsqueda de similitud: {e}")
            return []

    def get_available_tables(self) -> list[str]:
        """
        Obtiene una lista de nombres de tablas únicas que han sido añadidas.
        """
        try:
            # Obtener todos los documentos almacenados
            # El método .get() sin filtros devuelve todo
            all_docs = self.vector_store.get()
            
            if not all_docs or not all_docs.get("metadatas"):
                return []

            # Extraer los nombres de las tablas de los metadatos y eliminar duplicados
            table_names = {
                meta['table_name'] 
                for meta in all_docs["metadatas"] 
                if 'table_name' in meta
            }
            return sorted(list(table_names))
        except Exception as e:
            print(f"❌ Error obteniendo la lista de tablas: {e}")
            return []

    def query_openai(self, text: str) -> str:
        """Método de prueba para verificar la conexión con OpenAI."""
        # Este es un método simple para el health check, no usa el LLM directamente
        # pero confirma que la configuración de embeddings (que usa la API key) es válida.
        try:
            self.embeddings.embed_query(text)
            return "OK"
        except Exception as e:
            print(f"Error en query_openai (health check): {e}")
            return f"Error: {e}"