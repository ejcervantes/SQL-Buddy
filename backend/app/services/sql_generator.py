from typing import Dict, Any
from app.config import settings
from app.services.rag import RAGService

class SQLGeneratorService:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    def generate_sql_query(self, question: str) -> Dict[str, str]:
        """
        Genera una consulta SQL basada en una pregunta en lenguaje natural
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Diccionario con SQL, explicación y optimización
        """
        try:
            # Obtener contexto relevante
            context = self.rag_service.get_context_for_sql_generation(question)
            
            # Construir prompt para el LLM
            prompt = self._build_sql_prompt(question, context)
            
            # Consultar al LLM
            llm_response = self.rag_service.query_openai(prompt)
            
            # Parsear la respuesta
            result = self._parse_llm_response(llm_response)
            
            # Validar SQL generado
            validation = self.validate_sql(result["sql"])
            if not validation["is_valid"]:
                result["sql"] = f"-- SQL con errores de sintaxis:\n{result['sql']}\n\n-- Errores detectados:\n{validation['errors']}"
            
            return result
            
        except Exception as e:
            print(f"❌ Error generando SQL: {e}")
            return {
                "sql": "SELECT 'Error generando consulta SQL' as error;",
                "explanation": f"Ocurrió un error al generar la consulta: {str(e)}",
                "optimization": "No se pueden proporcionar sugerencias de optimización debido al error."
            }

    def _build_sql_prompt(self, question: str, context: str) -> str:
        """
        Construye el prompt para el LLM
        
        Args:
            question: Pregunta del usuario
            context: Contexto de la base de datos
            
        Returns:
            Prompt completo para el LLM
        """
        prompt = f"""
Eres un experto en SQL y bases de datos. Tu tarea es generar consultas SQL basadas en preguntas en lenguaje natural.

CONTEXTO DE LA BASE DE DATOS:
{context}

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES:
1. Analiza la pregunta y el contexto de la base de datos
2. Genera una consulta SQL válida y eficiente
3. Proporciona una explicación clara de lo que hace la consulta
4. Sugiere optimizaciones para mejorar el rendimiento

RESPONDE EN EL SIGUIENTE FORMATO:

```sql
-- Aquí va tu consulta SQL
SELECT columnas FROM tabla WHERE condiciones;
```

**Explicación:**
Explica qué hace la consulta y cómo funciona.

**Optimización:**
Sugiere mejoras de rendimiento, índices, o alternativas más eficientes.

IMPORTANTE:
- Usa solo las tablas y columnas mencionadas en el contexto
- Genera SQL estándar compatible con la mayoría de bases de datos
- Incluye comentarios explicativos en el SQL
- Sé específico en las explicaciones
"""
        return prompt

    def _parse_llm_response(self, llm_response: str) -> Dict[str, str]:
        """
        Parsea la respuesta del LLM para extraer SQL, explicación y optimización
        
        Args:
            llm_response: Respuesta completa del LLM
            
        Returns:
            Diccionario con SQL, explicación y optimización
        """
        try:
            # Buscar el bloque SQL
            sql_start = llm_response.find("```sql")
            sql_end = llm_response.find("```", sql_start + 6)
            
            if sql_start != -1 and sql_end != -1:
                sql = llm_response[sql_start + 6:sql_end].strip()
            else:
                # Si no hay bloques de código, buscar líneas que empiecen con SELECT, INSERT, etc.
                lines = llm_response.split('\n')
                sql_lines = []
                for line in lines:
                    line = line.strip()
                    if line.upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH')):
                        sql_lines.append(line)
                sql = '\n'.join(sql_lines) if sql_lines else "SELECT 'No se pudo generar SQL' as error;"
            
            # Extraer explicación y optimización
            explanation = ""
            optimization = ""
            
            # Buscar secciones por palabras clave
            if "**Explicación:**" in llm_response:
                exp_start = llm_response.find("**Explicación:**") + 16
                exp_end = llm_response.find("**", exp_start)
                if exp_end != -1:
                    explanation = llm_response[exp_start:exp_end].strip()
                else:
                    explanation = llm_response[exp_start:].strip()
            
            if "**Optimización:**" in llm_response:
                opt_start = llm_response.find("**Optimización:**") + 16
                opt_end = llm_response.find("**", opt_start)
                if opt_end != -1:
                    optimization = llm_response[opt_start:opt_end].strip()
                else:
                    optimization = llm_response[opt_start:].strip()
            
            # Valores por defecto si no se encontraron
            if not explanation:
                explanation = "La consulta SQL generada procesa los datos según la pregunta del usuario."
            
            if not optimization:
                optimization = "Considera crear índices en las columnas utilizadas en las cláusulas WHERE y JOIN para mejorar el rendimiento."
            
            return {
                "sql": sql,
                "explanation": explanation,
                "optimization": optimization
            }
            
        except Exception as e:
            print(f"Error parseando respuesta del LLM: {e}")
            return {
                "sql": "SELECT 'Error parseando respuesta' as error;",
                "explanation": f"Error al procesar la respuesta del LLM: {str(e)}",
                "optimization": "No se pueden proporcionar sugerencias de optimización."
            }

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Valida básicamente la sintaxis SQL
        
        Args:
            sql: Consulta SQL a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        try:
            # Validación básica de sintaxis
            sql_upper = sql.upper().strip()
            
            # Verificar que empiece con palabras clave válidas
            valid_start = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']
            starts_valid = any(sql_upper.startswith(start) for start in valid_start)
            
            # Verificar que termine con punto y coma
            ends_semicolon = sql.strip().endswith(';')
            
            # Verificar paréntesis balanceados
            open_parens = sql.count('(')
            close_parens = sql.count(')')
            balanced_parens = open_parens == close_parens
            
            is_valid = starts_valid and ends_semicolon and balanced_parens
            
            errors = []
            if not starts_valid:
                errors.append("La consulta debe empezar con SELECT, INSERT, UPDATE, DELETE o WITH")
            if not ends_semicolon:
                errors.append("La consulta debe terminar con punto y coma (;)")
            if not balanced_parens:
                errors.append("Los paréntesis no están balanceados")
            
            return {
                "is_valid": is_valid,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Error en la validación: {str(e)}"
            }
