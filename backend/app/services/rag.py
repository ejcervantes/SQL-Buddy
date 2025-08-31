import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_community.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'} # Usar 'cuda' si hay GPU disponible
        )
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=0.1
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def add_table_metadata(self, table_name: str, schema_info: str, description: str) -> bool:
        """
        Añade metadatos de una tabla a la base vectorial
        
        Args:
            table_name: Nombre de la tabla
            schema_info: Información del esquema de la tabla
            description: Descripción de la tabla
            
        Returns:
            True si se añadió exitosamente, False en caso contrario
        """
        try:
            # Crear documento con metadatos de la tabla
            content = f"Tabla: {table_name}\nEsquema: {schema_info}\nDescripción: {description}"
            
            # Dividir en chunks si es muy largo
            chunks = self.text_splitter.split_text(content)
            
            # Crear documentos con metadatos
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "table_name": table_name,
                        "schema_info": schema_info,
                        "description": description,
                        "chunk_id": i,
                        "type": "table_metadata"
                    }
                )
                documents.append(doc)
            
            # Añadir a la base vectorial
            self.vector_store.add_documents(documents)
            
            print(f"✅ Metadatos de tabla '{table_name}' añadidos a la base vectorial")
            return True
            
        except Exception as e:
            print(f"❌ Error añadiendo metadatos de tabla: {e}")
            return False

    def search_relevant_tables(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca tablas relevantes basándose en la pregunta del usuario
        
        Args:
            question: Pregunta del usuario
            top_k: Número máximo de resultados a retornar
            
        Returns:
            Lista de resultados con contenido y metadatos
        """
        try:
            # Realizar búsqueda de similitud
            results = self.vector_store.similarity_search_with_score(
                question, 
                k=top_k
            )
            
            # Formatear resultados
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            print(f"🔍 Encontradas {len(formatted_results)} tablas relevantes")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error en búsqueda de tablas: {e}")
            return []

    def get_context_for_sql_generation(self, question: str) -> str:
        """
        Obtiene el contexto relevante para generar SQL
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Contexto formateado con información de tablas relevantes
        """
        try:
            # Buscar tablas relevantes
            relevant_tables = self.search_relevant_tables(question, top_k=3)
            
            if not relevant_tables:
                return "No se encontraron tablas relevantes para la consulta."
            
            # Construir contexto
            context = "Contexto de la base de datos:\n\n"
            for i, result in enumerate(relevant_tables, 1):
                context += f"Tabla {i}:\n{result['content']}\n\n"
            
            return context
            
        except Exception as e:
            print(f"❌ Error obteniendo contexto: {e}")
            return "Error obteniendo contexto de la base de datos."

    def query_openai(self, prompt: str) -> str:
        """
        Consulta al modelo OpenAI GPT con un prompt específico
        
        Args:
            prompt: Prompt para enviar al LLM
            
        Returns:
            Respuesta del LLM
        """
        try:
            # Enviar prompt al LLM
            response = self.llm.invoke(prompt)
            
            # Extraer contenido de la respuesta
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            print(f"Error consultando OpenAI: {e}")
            return f"Error al generar respuesta: {str(e)}"
