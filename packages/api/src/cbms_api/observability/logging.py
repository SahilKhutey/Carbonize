"""
cbms_api/observability/logging.py

Structured logging with structlog.

All logs are JSON-formatted for machine parsing (prod) or pretty-printed (dev).
Provides:
  - configure_logging()          — call once at startup
  - set_request_context()        — call per-request (middleware)
  - clear_request_context()      — call at end of request
  - log_performance(operation)   — decorator to log function duration
  - LogContext                   — context-manager for temporary extra fields
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, Generator, Optional

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars


# ---------------------------------------------------------------------------
# Module-level context vars (request-scoped)
# ---------------------------------------------------------------------------

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
org_id_var: ContextVar[Optional[str]] = ContextVar("org_id", default=None)

_CONFIGURED = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def configure_logging(*, env: str = "development", log_level: str = "INFO") -> None:
    """
    Configure structlog for the entire application.

    Call ONCE at startup before any logging occurs.

    Args:
        env:       "prod" → JSON output; anything else → coloured dev console.
        log_level: Python log level string ("DEBUG", "INFO", etc.)
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure Python stdlib root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
        force=True,
    )

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Build processor chain
    shared_processors: list = [
        merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if env == "prod":
        final_renderer = structlog.processors.JSONRenderer()
    else:
        final_renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, final_renderer],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _CONFIGURED = True


def get_logger(name: str = __name__) -> Any:
    """Return a structlog logger. Alias for structlog.get_logger."""
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Request context helpers
# ---------------------------------------------------------------------------


def set_request_context(
    request_id: str,
    *,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
) -> None:
    """Bind request-scoped context to the current async task/thread."""
    request_id_var.set(request_id)
    user_id_var.set(user_id)
    org_id_var.set(org_id)

    ctx: dict[str, Any] = {"request_id": request_id}
    if user_id:
        ctx["user_id"] = user_id
    if org_id:
        ctx["org_id"] = org_id
    if path:
        ctx["path"] = path
    if method:
        ctx["method"] = method

    bind_contextvars(**ctx)


def clear_request_context() -> None:
    """Clear all bound context variables at end of request."""
    clear_contextvars()
    request_id_var.set(None)
    user_id_var.set(None)
    org_id_var.set(None)


# ---------------------------------------------------------------------------
# Performance decorator
# ---------------------------------------------------------------------------


def log_performance(operation: str) -> Callable:
    """
    Decorator that logs the duration of a function call.

    Usage::

        @log_performance("simulation.run")
        def run_simulation(...): ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = structlog.get_logger(func.__module__)
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                log.info(
                    "operation_completed",
                    operation=operation,
                    function=func.__name__,
                    duration_ms=round(elapsed_ms, 2),
                    status="success",
                )
                return result
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log.error(
                    "operation_failed",
                    operation=operation,
                    function=func.__name__,
                    duration_ms=round(elapsed_ms, 2),
                    error=str(exc),
                    error_type=type(exc).__name__,
                    exc_info=True,
                )
                raise
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


@contextmanager
def LogContext(**kwargs: Any) -> Generator[None, None, None]:
    """
    Context manager that temporarily binds extra fields to log context.

    Usage::

        with LogContext(simulation_id=sim_id, phase="kinetics"):
            run_kinetics(...)
    """
    bind_contextvars(**kwargs)
    try:
        yield
    finally:
        # Only unbind the keys we added
        from structlog.contextvars import get_contextvars
        ctx = get_contextvars()
        for k in kwargs:
            ctx.pop(k, None)
        clear_contextvars()
        bind_contextvars(**ctx)
