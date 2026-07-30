"""
Streaming analytics configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # ─── Application ───────────────────────────────────────
    APP_NAME: str = "Carbonize Streaming Analytics"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    # ─── Server ────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    CORS_ORIGINS: List[str] = ["*"]
    
    # ─── Kafka ─────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_CLIENT_ID: str = "carbonize-streaming"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISMS: Optional[str] = None
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None
    
    # ─── Topics ────────────────────────────────────────────
    TOPIC_TELEMETRY: str = "carbonize.telemetry"
    TOPIC_DETECTIONS: str = "carbonize.detections"
    TOPIC_ALERTS: str = "carbonize.alerts"
    TOPIC_TELEMETRY_PROCESSED: str = "carbonize.telemetry.processed"
    TOPIC_DETECTIONS_PROCESSED: str = "carbonize.detections.processed"
    TOPIC_ANOMALIES: str = "carbonize.anomalies"
    TOPIC_AGGREGATES: str = "carbonize.aggregates"
    TOPIC_DLQ: str = "carbonize.dlq"
    
    # ─── Consumer settings ─────────────────────────────────
    CONSUMER_GROUP: str = "carbonize-streaming"
    CONSUMER_AUTO_OFFSET_RESET: str = "latest"
    MAX_POLL_RECORDS: int = 500
    SESSION_TIMEOUT_MS: int = 30000
    
    # ─── Producer settings ─────────────────────────────────
    PRODUCER_ACKS: str = "all"
    PRODUCER_COMPRESSION: str = "lz4"
    PRODUCER_BATCH_SIZE: int = 16384
    PRODUCER_LINGER_MS: int = 5
    
    # ─── Schema Registry ───────────────────────────────────
    SCHEMA_REGISTRY_URL: str = "http://schema-registry:8081"
    USE_AVRO: bool = True
    
    # ─── Time-series DB ────────────────────────────────────
    INFLUXDB_URL: str = "http://influxdb:8086"
    INFLUXDB_TOKEN: str = "carbonize-token"
    INFLUXDB_ORG: str = "carbonize"
    INFLUXDB_BUCKET: str = "carbonize_metrics"
    
    # ─── WebSocket ─────────────────────────────────────────
    WS_MAX_CONNECTIONS: int = 10000
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    WS_FANOUT_WORKERS: int = 4
    
    # ─── Windowing ─────────────────────────────────────────
    DEFAULT_WINDOW_SECONDS: int = 60
    WATERMARK_LAG_SECONDS: int = 5
    ALLOWED_LATENESS_SECONDS: int = 30
    
    # ─── Anomaly Detection ─────────────────────────────────
    ANOMALY_Z_THRESHOLD: float = 3.0
    ANOMALY_CONTAMINATION: float = 0.05
    ANOMALY_WINDOW_SIZE: int = 100
    
    # ─── Flink ─────────────────────────────────────────────
    FLINK_JOBMANAGER_URL: str = "http://flink-jobmanager:8081"
    FLINK_PARALLELISM: int = 4
    
    # ─── Monitoring ────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
