import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    # Conexión a Postgres/Supabase. Es la fuente del esquema (introspección) y
    # también donde se almacena la base vectorial (pgvector). Obligatoria.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    # Esquema de Postgres a introspectar (normalmente "public").
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public")
    # Token opcional para proteger el endpoint POST /resync. Si está vacío, el
    # endpoint queda abierto (útil en desarrollo).
    RESYNC_TOKEN: str = os.getenv("RESYNC_TOKEN", "")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(',') if os.getenv("ALLOWED_ORIGINS") != "*" else ["*"]

    def validate(self) -> bool:
        is_valid = True
        if not self.OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY no está configurada.")
            is_valid = False
        return is_valid

# Instancia global de configuración
settings = Settings()
