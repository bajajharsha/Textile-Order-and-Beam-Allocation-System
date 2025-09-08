"""
Application settings and configuration management
Layer 5: Cross-Cutting Concerns
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = "Textile Order & Beam Allocation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"


settings = Settings()
