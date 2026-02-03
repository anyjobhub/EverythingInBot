"""
Configuration Management for EverythingInBot
Loads environment variables and provides app-wide settings
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    TELEGRAM_WEBHOOK_PATH: str = "/webhook"
    
    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_AI_API_KEY: Optional[str] = os.getenv("GOOGLE_AI_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Breach Check
    XPOSEDORNOT_API_KEY: Optional[str] = os.getenv("XPOSEDORNOT_API_KEY")
    
    # Payment Gateways
    RAZORPAY_KEY_ID: Optional[str] = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: Optional[str] = os.getenv("RAZORPAY_KEY_SECRET")
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_GUEST: int = 1  # requests per day
    RATE_LIMIT_FREE: int = 5   # requests per day
    RATE_LIMIT_PRO: int = -1   # unlimited
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_DOCUMENT_TYPES: list = ["application/pdf", "application/msword"]
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("REDIS_URL", "")
    CELERY_RESULT_BACKEND: str = os.getenv("REDIS_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_webhook_url() -> str:
    """Get full webhook URL for Telegram"""
    # This will be set as environment variable in Render
    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
    return f"{base_url}{settings.TELEGRAM_WEBHOOK_PATH}/{settings.TELEGRAM_BOT_TOKEN}"
