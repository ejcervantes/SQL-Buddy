from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from app.config import settings
from app.services.rag_service import RAGServicePGVector

class SQLResponse(BaseModel):
    """Define la estructura de la respuesta JSON que esperamos del LLM."""
    sql: str = Field(description="La consulta SQL generada.")
    explanation: str = Field(description="Una explicación de la consulta SQL.")
    optimization_suggestion: str = Field(description="Una sugerencia para optimizar la consulta, como la creación de un índice.")

class SQLGeneratorService:
    """
    Servicio para generar consultas SQL a partir de preguntas en lenguaje natural.
    """
    def __init__(self, rag_service: RAGServicePGVector):
        self.rag_service = rag_service
        self.llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, openai_api_key=settings.OPENAI_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=SQLResponse)
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self):
        """
        Crea el template del prompt, incluyendo instrucciones de formato del parser.
        """
        template = """
        Eres un asistente experto en bases de datos. Tu tarea es generar una consulta SQL, una explicación clara y una sugerencia de optimización, basada en los esquemas de tabla proporcionados y la pregunta del usuario. Ten en cuenta que la base de datos se maneja en PosgreSQL. Nunca devulvas un punto y coma (;) al final de las querys generadas.

        Reglas:
        1.  Analiza el contexto y la pregunta para generar la consulta SQL más precisa posible.
        2.  Usa los nombres de tablas y columnas exactamente como se definen en los esquemas.
        3.  Proporciona una sugerencia de optimización útil, como la creación de un índice en una columna usada en un `WHERE` o `JOIN`. Si no hay una optimización obvia, responde con "No se sugiere ninguna optimización específica.".
        4.  Si la pregunta no se puede responder con los esquemas, la `sql_query` debe ser "ERROR: La pregunta no se puede responder con el contexto proporcionado." y la explicación debe indicar por qué.
        5.  TU SALIDA DEBE SER ÚNICAMENTE UN OBJETO JSON VÁLIDO. No incluyas texto antes o después del JSON. No uses formato markdown como ```json.
        
        Contexto (Esquemas de Tablas):
        {context}

        Pregunta del usuario:
        {question}
        
        Sigue estrictamente las siguientes instrucciones de formato:
        {format_instructions}
        """
        return ChatPromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def generate_sql_query(self, question: str) -> dict:
        """
        Genera la consulta SQL, explicación y optimización de forma robusta.
        """
        chain = (
            {"context": self.rag_service.get_context_for_sql_generation, "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | self.parser
        )
        
        try:
            print("🧠 Invocando la cadena de generación de SQL...")
            response = chain.invoke(question)
            print("✅ Respuesta del LLM parseada correctamente.")
            return {
                "sql": response.sql,
                "explanation": response.explanation,
                "optimization": response.optimization_suggestion
            }
        except Exception as e:
            # Clasifica el error para mostrar una causa clara en vez de un genérico.
            detail = str(e)
            low = detail.lower()
            if "account_deactivated" in low or "invalid_api_key" in low or "401" in low or "authentication" in low:
                summary = "ERROR: OpenAI authentication/account problem (check the API key and that the account is active)."
            elif "insufficient_quota" in low or "429" in low or "rate limit" in low or "quota" in low:
                summary = "ERROR: OpenAI quota/rate limit reached (check billing and usage limits)."
            elif "model" in low and ("does not exist" in low or "not found" in low or "do not have access" in low):
                summary = "ERROR: The configured model is not available for this account (check OPENAI_MODEL)."
            else:
                summary = "ERROR: The language model returned an invalid or unreadable response."

            print(f"❌ Error generando SQL: {detail}")
            return {
                "sql": summary,
                "explanation": f"The SQL query could not be generated. Error details: {detail}",
                "optimization": "Not available due to the error above."
            }
