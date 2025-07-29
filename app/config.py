import os
from typing import List
from pydantic_settings import BaseSettings
from slowapi import Limiter
from slowapi.util import get_remote_address


class Settings(BaseSettings):
    # Server Configuration
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("NODE_ENV", "development") == "development"
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")
    JWT_EXPIRES_IN: str = os.getenv("JWT_EXPIRES_IN", "24h")
    JWT_ALGORITHM: str = "HS256"
    
    # CORS Configuration
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
        return [origin.strip() for origin in origins_str.split(",")]
    
    # Rate Limiting
    RATE_LIMIT_WINDOW_MS: int = int(os.getenv("RATE_LIMIT_WINDOW_MS", "900000"))  # 15 minutes
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    
    # OpenAI Configuration (for future LLM integration)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Database Configuration (for future use)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "chatbot_orders")
    DB_USER: str = os.getenv("DB_USER", "chatbot")
    DB_PASS: str = os.getenv("DB_PASS", "password")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    class Config:
        extra = "allow"  # Allow extra fields
        env_file = ".env"


# Initialize settings
settings = Settings()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/15minutes"]  # Default global rate limit
)
