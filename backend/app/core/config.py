"""
Core configuration for the ACI Dashboard API
Handles environment variables and application settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/acidashboard")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "aSK1LtZz7jqianX3Xz1AEcSjHQRbnY30tNlDptwu6T2DOxDuKyzcjOriZYWNNCoM")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "SxYjdAjtiJo4jDC1CW8zZ/0NFV55Qeje4WevX5yDOcn9dwujUoQ6EMeWYvfLzNEb")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ACI Dashboard API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise-grade dashboard with role-based access control"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Global settings instance
settings = Settings()