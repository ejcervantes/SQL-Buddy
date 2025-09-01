from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.services.rag_chroma import RAGServiceChroma

class SQLGeneratorService:
    """
    Servicio para generar consultas SQL a partir de preguntas en lenguaje natural.
    """
    def __init__(self, rag_service: RAGServiceChroma):
        """
        Inicializa el servicio con el modelo de lenguaje y el servicio RAG.
        """
        self.rag_service = rag_service
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self):
        """
        Crea el template del prompt para la generación de SQL.
        """
        template = """
        Eres un asistente experto en bases de datos. Tu tarea es generar una consulta SQL y una explicación clara basada en los esquemas de tabla proporcionados y la pregunta del usuario.

        Reglas:
        1.  Analiza el contexto y la pregunta para generar la consulta SQL más precisa posible.
        2.  Usa los nombres de tablas y columnas exactamente como se definen en los esquemas.
        3.  Crea una explicación breve y clara de cómo funciona la consulta SQL.
        4.  Si la pregunta no se puede responder con los esquemas, la consulta SQL debe ser "ERROR" y la explicación debe indicar por qué.

        Contexto (Esquemas de Tablas):
        {context}

        Pregunta del usuario:
        {question}
        
        Devuelve tu respuesta en un formato JSON con las siguientes claves: "sql_query", "explanation".
        """
        return ChatPromptTemplate.from_template(template)

    def generate_sql_query(self, question: str) -> dict:
        """
        Genera la consulta SQL, explicación y optimización.
        """
        parser = JsonOutputParser()

        chain = (
            {
                "context": self.rag_service.get_context_for_sql_generation, 
                "question": RunnablePassthrough()
            }
            | self.prompt_template
            | self.llm
            | parser
        )
        
        response_json = chain.invoke(question)

        return {
            "sql": response_json.get("sql_query", "ERROR: No se pudo generar la consulta."),
            "explanation": response_json.get("explanation", "No se pudo generar una explicación."),
            "optimization": "Aquí se mostrarán sugerencias de optimización, como la creación de índices."
        }
