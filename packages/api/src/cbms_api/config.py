"""
Application settings with auth configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    environment: str = Field(default="development", description="dev|staging|prod")
    debug: bool = False
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/biomimetic_db",
        description="Async PostgreSQL URL"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_pool_recycle: int = 3600
    
    # Redis (for rate limiting, caching)
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    jwt_secret: str = Field(default="supersecretsupersecretsupersecretsupersecret", min_length=32, description="HMAC secret (32+ bytes)")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "cbms.in"
    jwt_audience: str = "cbms-api"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    
    # Password
    password_min_length: int = 12
    bcrypt_cost_factor: int = 12
    
    # MFA
    mfa_required_roles: list[str] = ["owner", "admin"]
    mfa_issuer: str = "CBMS"
    mfa_backup_codes_count: int = 10
    
    # Rate limiting
    rate_limit_login_per_minute: int = 5
    rate_limit_refresh_per_minute: int = 30
    rate_limit_simulation_per_minute: int = 10
    rate_limit_default_per_minute: int = 1000
    
    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    cors_allow_credentials: bool = True
    
    # Audit
    audit_log_retention_days: int = 2555  # 7 years
    
    # Security
    rate_limit_enabled: bool = True
    mfa_enabled: bool = True

    # Observability
    log_level: str = Field(default="INFO", description="Root log level: DEBUG|INFO|WARNING|ERROR")
    sentry_dsn: str = Field(default="", description="Sentry DSN (empty = disabled)")
    app_version: str = Field(default="0.1.0", description="Application version for Sentry release tag")
    metrics_enabled: bool = Field(default=True, description="Enable Prometheus /metrics endpoint")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
