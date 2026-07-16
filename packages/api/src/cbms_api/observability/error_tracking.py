"""
cbms_api/observability/error_tracking.py

Sentry error tracking integration.

Features:
  - Opt-in: no-ops when SENTRY_DSN is empty
  - Sensitive data scrubbing (Authorization header, password fields)
  - Skips health-check endpoints and the test environment
  - Explicit helpers for user context and manual error reporting
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


def init_sentry() -> None:
    """
    Initialise Sentry SDK from ``settings.sentry_dsn``.

    Call ONCE at application startup after :func:`configure_logging`.
    Safe to call when DSN is empty — will just log a notice and return.
    """
    from cbms_api.config import get_settings
    settings = get_settings()

    if not settings.sentry_dsn:
        logger.info("sentry_disabled", reason="SENTRY_DSN not configured")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=settings.app_version,
            # Performance: trace 10 % of requests
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            integrations=[
                FastApiIntegration(),
                CeleryIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.WARNING,   # capture WARNING+ as breadcrumbs
                    event_level=logging.ERROR,  # ERROR+ as Sentry events
                ),
            ],
            before_send=_before_send,
            before_send_transaction=_before_send_transaction,
            enable_tracing=True,
        )
        logger.info(
            "sentry_initialized",
            environment=settings.environment,
            release=settings.app_version,
        )
    except ImportError:
        logger.warning("sentry_sdk_not_installed", advice="pip install sentry-sdk[fastapi,celery,sqlalchemy,redis]")


# ---------------------------------------------------------------------------
# Event filters
# ---------------------------------------------------------------------------

_SENSITIVE_KEYS = frozenset({"password", "new_password", "current_password", "secret", "token", "access_token", "refresh_token"})


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Scrub sensitive data; drop health-check and test events."""
    from cbms_api.config import get_settings
    settings = get_settings()

    # Never send events in test env
    if settings.environment in ("test", "testing"):
        return None

    # Drop health-check events
    url: str = event.get("request", {}).get("url", "")
    if url.endswith(("/health", "/healthz", "/ready", "/metrics")):
        return None

    # Scrub Authorization header
    headers: dict = event.get("request", {}).get("headers", {})
    if "Authorization" in headers:
        headers["Authorization"] = "Bearer [filtered]"

    # Scrub password fields from request body
    data: dict = event.get("request", {}).get("data", {})
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key.lower() in _SENSITIVE_KEYS:
                data[key] = "[filtered]"

    return event


def _before_send_transaction(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Drop transactions for noisy endpoints."""
    tx: str = event.get("transaction", "")
    if any(tx.endswith(ep) for ep in ("/health", "/healthz", "/ready", "/metrics")):
        return None
    return event


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------


def set_sentry_user(user_id: str, org_id: str, email: Optional[str] = None) -> None:
    """Attach user identity to all Sentry events in this request scope."""
    try:
        import sentry_sdk
        sentry_sdk.set_user({"id": user_id, "email": email})
        sentry_sdk.set_tag("org_id", org_id)
    except ImportError:
        pass


def clear_sentry_user() -> None:
    """Remove user identity from Sentry scope."""
    try:
        import sentry_sdk
        sentry_sdk.set_user(None)
    except ImportError:
        pass


def report_error(error: Exception, context: Optional[dict[str, Any]] = None) -> None:
    """Manually capture an exception and send it to Sentry."""
    try:
        import sentry_sdk
        if context:
            for k, v in context.items():
                sentry_sdk.set_tag(k, str(v))
        sentry_sdk.capture_exception(error)
    except ImportError:
        logger.error("sentry_capture_failed_no_sdk", error=str(error))


def report_message(message: str, level: str = "info", context: Optional[dict[str, Any]] = None) -> None:
    """Manually send an informational message to Sentry."""
    try:
        import sentry_sdk
        if context:
            for k, v in context.items():
                sentry_sdk.set_tag(k, str(v))
        sentry_sdk.capture_message(message, level=level)
    except ImportError:
        pass
