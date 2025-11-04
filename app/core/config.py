"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    # Default to SQLite for easy local development (no PostgreSQL needed)
    DATABASE_URL: str = "sqlite:///./resume_parser.db"
    ENVIRONMENT: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    MODEL_CACHE_DIR: str = "./models"
    USE_GPU: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

