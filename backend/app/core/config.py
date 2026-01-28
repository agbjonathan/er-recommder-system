"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database Configuration
    postgres_user: str = "er_user"
    postgres_password: str = "password"
    postgres_db: str = "er_recommender_db"
    postgres_host: str = "db"
    postgres_port: int = 5432
    
    # API Configuration
    api_secret_key: str = "your-secret-key-change-in-production"
    backend_port: int = 8000
    
    # Application Settings
    debug: bool = False
    environment: str = "production"
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
