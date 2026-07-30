"""
Carbonize Streaming Analytics - Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.producers.kafka_producer import kafka_producer
from app.processors.stream_processors import (
    telemetry_processor, detection_processor,
    aggregate_processor, anomaly_processor,
)
from app.processors.drift_processor import drift_processor
from app.storage.timeseries_db import timeseries_db
from app.api.stream_api import router as stream_router
from app.api.drift_api import router as drift_router

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    
    await kafka_producer.initialize()
    await timeseries_db.initialize()
    
    await telemetry_processor.start()
    await detection_processor.start()
    await aggregate_processor.start()
    await anomaly_processor.start()
    await drift_processor.start()
    
    yield
    
    logger.info("Shutting down streaming engine...")
    await telemetry_processor.consumer.stop()
    await detection_processor.consumer.stop()
    await aggregate_processor.consumer.stop()
    await anomaly_processor.consumer.stop()
    await drift_processor.consumer.stop()
    
    await kafka_producer.flush(timeout=10)
    await timeseries_db.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router, prefix="/api")
app.include_router(drift_router, prefix="/api")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "kafka_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    }
