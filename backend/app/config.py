"""Configuration management for AirPuff application."""

from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://airpuff:airpuff@localhost:5432/airpuff"
    timescaledb_url: str = "postgresql://airpuff:airpuff@localhost:5432/airpuff"

    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API Keys
    fli_rite_api_key: Optional[str] = None
    checkwx_api_key: Optional[str] = None
    
    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None

    # OIDC (Keycloak via cloudpuff)
    oidc_issuer: Optional[str] = None
    oidc_client_id: str = "airpuff-web"
    oidc_client_secret: Optional[str] = None
    oidc_redirect_uri: Optional[str] = None
    oidc_admin_roles: str = "admin,airpuff-admin"
    session_secret: str = "change-me-in-production"
    base_url: str = "http://localhost:25080"

    # Grafana
    grafana_url: str = "http://localhost:3000"
    grafana_username: str = "admin"
    grafana_password: str = "admin"
    
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
    log_level: str = "INFO"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 25080

    # Performance
    workers: int = 2
    max_requests: int = 1000
    max_requests_jitter: int = 100
    
    # WebSocket
    websocket_ping_interval: int = 25
    websocket_ping_timeout: int = 20

    @model_validator(mode="after")
    def apply_environment_defaults(self):
        """Apply environment-specific defaults after settings load."""

        if not self.oidc_issuer:
            env = (self.environment or "").strip().lower()
            host = "auth.cloudpuff.org" if env in {"production", "prod"} else "auth-dev.cloudpuff.org"
            self.oidc_issuer = f"https://{host}/realms/cloudpuff"

        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
