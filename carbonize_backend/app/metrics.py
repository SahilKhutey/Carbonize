"""
Production Metrics Module
Fixes Bottleneck B14: Silent degradation
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    Info, CollectorRegistry, generate_latest,
    CONTENT_TYPE_LATEST
)
import time
import psutil
import os
import asyncio
from typing import Callable
from functools import wraps


# ─── Registry ───────────────────────────────────────────────────────
REGISTRY = CollectorRegistry()


# ─── Inference Metrics ──────────────────────────────────────────────
INFERENCE_LATENCY = Histogram(
    'carbonize_inference_latency_seconds',
    'YOLO inference latency',
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
    registry=REGISTRY
)

INFERENCE_COUNT = Counter(
    'carbonize_inference_total',
    'Total inferences',
    ['model_version', 'status'],
    registry=REGISTRY
)

INFERENCE_QUEUE_SIZE = Gauge(
    'carbonize_inference_queue_size',
    'Pending tasks in inference queue',
    registry=REGISTRY
)

# ─── Telemetry Metrics ──────────────────────────────────────────────
TELEMETRY_INGESTED = Counter(
    'carbonize_telemetry_ingested_total',
    'Telemetry messages received',
    ['robot_id', 'status'],
    registry=REGISTRY
)

TELEMETRY_BACKPRESSURE = Gauge(
    'carbonize_telemetry_dropped_total',
    'Telemetry messages dropped due to backpressure',
    registry=REGISTRY
)

# ─── ROS Bridge Metrics ─────────────────────────────────────────────
ROS_FRAME_RATE = Gauge(
    'carbonize_ros_camera_fps',
    'Camera frame rate observed by ROS node',
    registry=REGISTRY
)

ROS_TF_LATENCY = Histogram(
    'carbonize_tf_lookup_seconds',
    'TF transform lookup latency',
    registry=REGISTRY
)

# ─── System Metrics ─────────────────────────────────────────────────
SYSTEM_CPU = Gauge(
    'carbonize_system_cpu_percent',
    'Process CPU usage',
    registry=REGISTRY
)

SYSTEM_MEMORY = Gauge(
    'carbonize_system_memory_rss',
    'Process RSS memory in bytes',
    registry=REGISTRY
)

GPU_UTIL = Gauge(
    'carbonize_gpu_utilization_percent',
    'GPU utilization (0-100)',
    registry=REGISTRY
)

GPU_MEMORY = Gauge(
    'carbonize_gpu_memory_used_bytes',
    'GPU memory used',
    registry=REGISTRY
)

# ─── Health Probe ───────────────────────────────────────────────────
class HealthProbe:
    """Composite health probe — liveness + readiness."""
    
    def __init__(self, name: str = "carbonize-backend"):
        self.name = name
        self._checks = {}
        self._start_time = time.time()
    
    def register(self, name: str, check_fn: Callable):
        """Register a check function (sync or async)."""
        self._checks[name] = check_fn
    
    async def liveness(self) -> dict:
        """Is the process alive?"""
        return {
            "status": "alive",
            "uptime_sec": time.time() - self._start_time,
            "pid": os.getpid()
        }
    
    async def readiness(self) -> dict:
        """Are dependencies (Redis, GPU, etc.) ready?"""
        results = {}
        overall_ok = True
        
        for name, fn in self._checks.items():
            try:
                if asyncio.iscoroutinefunction(fn):
                    ok = await fn()
                else:
                    ok = fn()
                results[name] = {"ok": bool(ok)}
                if not ok:
                    overall_ok = False
            except Exception as e:
                results[name] = {"ok": False, "error": str(e)}
                overall_ok = False
        
        return {
            "status": "ready" if overall_ok else "degraded",
            "checks": results
        }
    
    async def system_metrics(self) -> dict:
        """System-level metrics."""
        process = psutil.Process(os.getpid())
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_rss": process.memory_info().rss,
            "memory_vms": process.memory_info().vms,
            "threads": process.num_threads(),
            "open_fds": len(process.open_files()) if hasattr(process, 'open_files') else 0
        }


# ─── Decorator for auto-instrumentation ─────────────────────────────
def track_inference(model_version: str):
    """Decorator to auto-track inference metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = "success"
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                return result
            except Exception:
                status = "failed"
                raise
            finally:
                elapsed = time.perf_counter() - start
                INFERENCE_LATENCY.observe(elapsed)
                INFERENCE_COUNT.labels(model_version=model_version, status=status).inc()
        return wrapper
    return decorator
