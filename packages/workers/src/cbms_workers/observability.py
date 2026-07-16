"""
cbms_workers/observability.py

Celery worker observability — structured logging + Prometheus metrics.

Hooks into Celery signals to track:
  - Task start / success / failure / retry lifecycle
  - Queue depth (polled periodically)
  - Worker liveness
  - Stuck task detection

Usage:
    Import this module in your Celery app setup so that signals connect:

        from cbms_workers import observability  # noqa: F401  — side-effects only
"""

from __future__ import annotations

import logging
import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Metric definitions (local subset — avoids importing the full API package)
# These mirror the definitions in cbms_api.observability.metrics so that
# the worker process can update them independently.
# ---------------------------------------------------------------------------

try:
    from prometheus_client import Counter, Histogram, Gauge

    _celery_tasks_total = Counter(
        "cbms_celery_tasks_total",
        "Total Celery tasks processed",
        ["task_name", "queue", "status"],
    )
    _celery_task_duration_seconds = Histogram(
        "cbms_celery_task_duration_seconds",
        "Celery task execution duration in seconds",
        ["task_name", "queue"],
        buckets=(1, 5, 10, 30, 60, 300, 600, 1800, 3600),
    )
    _celery_queue_depth = Gauge(
        "cbms_celery_queue_depth",
        "Tasks waiting in a Celery queue",
        ["queue_name"],
    )
    _celery_active_workers = Gauge(
        "cbms_celery_active_workers",
        "Active Celery worker processes",
        ["queue_name"],
    )
    _celery_task_retries_total = Counter(
        "cbms_celery_task_retries_total",
        "Total Celery task retries due to transient failures",
        ["task_name", "queue"],
    )
    _celery_stuck_tasks = Gauge(
        "cbms_celery_stuck_tasks",
        "Tasks stuck in GENERATING beyond timeout",
        ["queue_name", "task_name"],
    )
    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False


def _get_queue(task_request: Any) -> str:
    try:
        return task_request.delivery_info.get("routing_key", "default")
    except Exception:
        return "default"


# ---------------------------------------------------------------------------
# Signal handlers — connected lazily to avoid import-order issues
# ---------------------------------------------------------------------------


def connect_signals() -> None:
    """
    Connect all Celery task signals.

    Call this after the Celery app is fully configured::

        from cbms_workers.observability import connect_signals
        connect_signals()
    """
    try:
        from celery import signals

        @signals.task_prerun.connect
        def on_task_prerun(sender=None, task_id=None, task=None, **kwargs) -> None:
            if task is not None:
                task._obs_start = time.perf_counter()
            logger.info(
                "celery_task_started",
                task_id=task_id,
                task_name=getattr(task, "name", "unknown"),
                retries=getattr(getattr(task, "request", None), "retries", 0),
            )

        @signals.task_success.connect
        def on_task_success(sender=None, result=None, **kwargs) -> None:
            task = sender
            if task is None:
                return
            duration = time.perf_counter() - getattr(task, "_obs_start", time.perf_counter())
            queue = _get_queue(task.request)

            if _METRICS_AVAILABLE:
                _celery_tasks_total.labels(
                    task_name=task.name, queue=queue, status="success"
                ).inc()
                _celery_task_duration_seconds.labels(
                    task_name=task.name, queue=queue
                ).observe(duration)

            logger.info(
                "celery_task_succeeded",
                task_id=task.request.id,
                task_name=task.name,
                queue=queue,
                duration_seconds=round(duration, 3),
            )

        @signals.task_failure.connect
        def on_task_failure(
            sender=None, task_id=None, exception=None, einfo=None, **kwargs
        ) -> None:
            task = sender
            duration = time.perf_counter() - getattr(task, "_obs_start", time.perf_counter()) if task else 0.0
            queue = _get_queue(task.request) if task else "unknown"
            task_name = getattr(task, "name", "unknown")

            max_retries = getattr(task, "max_retries", 0) or 0
            current_retries = getattr(getattr(task, "request", None), "retries", 0) or 0
            will_retry = current_retries < max_retries

            if _METRICS_AVAILABLE:
                status = "retry" if will_retry else "failure"
                _celery_tasks_total.labels(
                    task_name=task_name, queue=queue, status=status
                ).inc()
                if will_retry:
                    _celery_task_retries_total.labels(
                        task_name=task_name, queue=queue
                    ).inc()

            logger.error(
                "celery_task_failed",
                task_id=task_id,
                task_name=task_name,
                queue=queue,
                error=str(exception)[:200] if exception else None,
                error_type=type(exception).__name__ if exception else "unknown",
                will_retry=will_retry,
                duration_seconds=round(duration, 3),
            )

        @signals.task_retry.connect
        def on_task_retry(sender=None, reason=None, **kwargs) -> None:
            task = sender
            if task is None:
                return
            queue = _get_queue(task.request)
            if _METRICS_AVAILABLE:
                _celery_task_retries_total.labels(
                    task_name=task.name, queue=queue
                ).inc()
            logger.warning(
                "celery_task_retrying",
                task_name=task.name,
                task_id=task.request.id,
                reason=str(reason)[:200],
                attempt=task.request.retries,
            )

        @signals.worker_ready.connect
        def on_worker_ready(sender=None, **kwargs) -> None:
            import socket
            logger.info("celery_worker_ready", hostname=socket.gethostname())

        @signals.worker_shutdown.connect
        def on_worker_shutdown(sender=None, **kwargs) -> None:
            logger.info("celery_worker_shutdown")

        logger.info("celery_observability_signals_connected")

    except ImportError:
        logger.warning("celery_not_installed", advice="pip install celery")


# ---------------------------------------------------------------------------
# Queue depth updater — call from a periodic beat task
# ---------------------------------------------------------------------------


def update_queue_depths(broker_url: str, queue_names: list[str]) -> dict[str, int]:
    """
    Read queue depth from Redis broker and update Prometheus gauges.

    Args:
        broker_url:  Redis URL (same as Celery's broker_url setting).
        queue_names: List of queue names to poll.

    Returns:
        Mapping of queue_name → depth.
    """
    depths: dict[str, int] = {}
    try:
        from redis import Redis
        r = Redis.from_url(broker_url, socket_connect_timeout=2)
        for name in queue_names:
            depth = int(r.llen(name))
            depths[name] = depth
            if _METRICS_AVAILABLE:
                _celery_queue_depth.labels(queue_name=name).set(depth)
        logger.debug("queue_depths_updated", depths=depths)
    except Exception as exc:
        logger.warning("queue_depth_update_failed", error=str(exc)[:200])
    return depths
