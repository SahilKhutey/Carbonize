"""Prometheus metrics endpoint + health probes."""

from fastapi import APIRouter, Response
from app.metrics import (
    REGISTRY, generate_latest, CONTENT_TYPE_LATEST,
    HealthProbe, SYSTEM_CPU, SYSTEM_MEMORY
)
import asyncio
import time

router = APIRouter()
health = HealthProbe("carbonize-backend")

# Register checks
async def check_redis():
    try:
        from app.redis_client import get_redis
        r = await get_redis()
        return await r.ping()
    except Exception:
        return False

async def check_mlflow():
    return True

health.register("redis", check_redis)
health.register("mlflow", check_mlflow)


@router.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    # Update system metrics
    import psutil, os
    process = psutil.Process(os.getpid())
    SYSTEM_CPU.set(process.cpu_percent())
    SYSTEM_MEMORY.set(process.memory_info().rss)
    
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/v1/health/live")
async def liveness():
    """Kubernetes-style liveness probe."""
    return await health.liveness()


@router.get("/v1/health/ready")
async def readiness():
    """Kubernetes-style readiness probe."""
    return await health.readiness()


@router.get("/v1/health")
async def health_combined():
    """Combined health response."""
    return {
        "liveness": await health.liveness(),
        "readiness": await health.readiness(),
        "system": await health.system_metrics()
    }
