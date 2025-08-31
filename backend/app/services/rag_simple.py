import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

class RAGServiceSimple:
    def __init__(self):
        # Usar OpenAI embeddings en lugar de HuggingFace
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
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
        """
        try:
            content = f"Tabla: {table_name}\nEsquema: {schema_info}\nDescripción: {description}"
            chunks = self.text_splitter.split_text(content)
            
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
            
            self.vector_store.add_documents(documents)
            print(f"✅ Metadatos de tabla '{table_name}' añadidos a la base vectorial")
            return True
            
        except Exception as e:
            print(f"❌ Error añadiendo metadatos de tabla: {e}")
            return False

    def search_relevant_tables(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca tablas relevantes basándose en la pregunta del usuario
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                question, 
                k=top_k
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error buscando tablas relevantes: {e}")
            return []

    def get_context_for_sql_generation(self, question: str) -> str:
        """
        Obtiene contexto relevante para la generación de SQL
        """
        try:
            relevant_tables = self.search_relevant_tables(question, top_k=5)
            
            if not relevant_tables:
                return "No hay información de tablas disponible."
            
            context = "INFORMACIÓN DE TABLAS DISPONIBLES:\n\n"
            for result in relevant_tables:
                context += f"• {result['content']}\n\n"
            
            return context
            
        except Exception as e:
            print(f"❌ Error obteniendo contexto: {e}")
            return "Error obteniendo contexto de la base de datos."

    def query_openai(self, prompt: str) -> str:
        """
        Consulta directamente a OpenAI
        """
        try:
            response = self.llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error consultando OpenAI: {e}")
            return f"Error al generar respuesta: {str(e)}"
