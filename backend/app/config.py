import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
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
