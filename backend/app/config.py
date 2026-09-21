import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "Synthetic User Research Platform")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./synthetic_users.db")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

settings = Settings()
