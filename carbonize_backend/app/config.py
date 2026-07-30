"""
Production configuration with Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # ─── Application ───────────────────────────────────────
    APP_NAME: str = "Carbonize ML Backend"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # ─── Server ────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "https://dashboard.carbonize.io"]
    
    # ─── Database ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql://carbonize:password@postgres:5432/carbonize"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # ─── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_MAX_CONNECTIONS: int = 50
    
    # ─── MLflow ────────────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    MLFLOW_S3_ENDPOINT_URL: Optional[str] = "http://minio:9000"
    MLFLOW_BUCKET: str = "carbonize-models"
    
    # ─── Celery ────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    
    # ─── Model Registry ────────────────────────────────────
    MODEL_REGISTRY_PATH: str = "/var/lib/carbonize/models"
    MODEL_CACHE_DIR: str = "/tmp/carbonize-model-cache"
    MAX_MODEL_LOAD_TIME: int = 60
    
    # ─── Inference ─────────────────────────────────────────
    INFERENCE_BATCH_SIZE: int = 8
    INFERENCE_TIMEOUT: int = 30
    GPU_DEVICE: str = "cuda"
    ENABLE_TENSORRT: bool = True
    TENSORRT_PRECISION: str = "fp16"
    
    # ─── Storage ───────────────────────────────────────────
    S3_BUCKET: str = "carbonize-data"
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: Optional[str] = None
    UPLOAD_DIR: str = "/var/lib/carbonize/uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    
    # ─── Auth ──────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    API_KEY_PREFIX: str = "ck_"
    
    # ─── Monitoring ────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    
    # ─── Rate Limiting ─────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # ─── Drift Detection ───────────────────────────────────
    DRIFT_CHECK_INTERVAL_HOURS: int = 6
    DRIFT_KS_THRESHOLD: float = 0.05
    DRIFT_PSI_THRESHOLD: float = 0.25
    
    # ─── Forecasting ───────────────────────────────────────
    FORECAST_DEFAULT_HORIZON: int = 24
    FORECAST_MAX_HORIZON: int = 168
    FORECAST_MODELS: List[str] = ["prophet", "arima", "lstm"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
