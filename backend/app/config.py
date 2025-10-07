"""Configuration management for AirPuff application."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://airpuff:airpuff@localhost:5432/airpuff"
    timescaledb_url: str = "postgresql://airpuff:airpuff@localhost:5432/airpuff"
    
    # API Keys
    fli_rite_api_key: Optional[str] = None
    checkwx_api_key: Optional[str] = None
    
    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # iMessage
    imessage_bridge_url: Optional[str] = None
    imessage_api_key: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # WebSocket
    websocket_ping_interval: int = 25
    websocket_ping_timeout: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
