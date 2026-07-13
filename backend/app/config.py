import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    # Cadena de conexión a Postgres para introspectar el esquema en vivo.
    # Si está vacía, la app usa metadata_seed.json como respaldo.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    # Esquema de Postgres a introspectar (normalmente "public").
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public")
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
