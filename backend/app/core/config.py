"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "Er Recommender System"
    APP_ENV: str = "local"
    database_url: str

    class Config:
        env_file = ".env"
        


settings = Settings()
