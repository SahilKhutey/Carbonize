"""
cbms_api/observability/__init__.py

Public API of the observability package.
Import from here to avoid reaching into sub-modules directly.
"""

from cbms_api.observability.logging import configure_logging, set_request_context, clear_request_context
from cbms_api.observability.metrics import (
    REGISTRY,
    record_http_request,
    record_simulation_submitted,
    record_simulation_completed,
    record_celery_task,
    http_requests_in_flight,
    ws_active_connections,
    ws_messages_total,
    auth_login_total,
)
from cbms_api.observability.error_tracking import init_sentry, report_error
from cbms_api.observability.middleware import ObservabilityMiddleware

__all__ = [
    "configure_logging",
    "set_request_context",
    "clear_request_context",
    "init_sentry",
    "report_error",
    "ObservabilityMiddleware",
    "REGISTRY",
    "record_http_request",
    "record_simulation_submitted",
    "record_simulation_completed",
    "record_celery_task",
    "http_requests_in_flight",
    "ws_active_connections",
    "ws_messages_total",
    "auth_login_total",
]
