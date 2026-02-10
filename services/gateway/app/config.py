"""Configuration for gateway service."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Gateway service settings."""
    
    # Service URLs
    auth_service_url: str = "http://auth:8001"
    tenant_service_url: str = "http://tenant:8002"
    ingestion_service_url: str = "http://ingestion:8003"
    workflows_service_url: str = "http://workflows:8004"
    budgets_service_url: str = "http://budgets:8005"
    query_service_url: str = "http://query:8006"
    integrations_service_url: str = "http://integrations:8007"
    
    # Gateway settings
    port: int = 8000
    workers: int = 4
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
