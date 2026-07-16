"""
cbms_api/observability/middleware.py

ObservabilityMiddleware — wraps every FastAPI request with:

  1. Request ID generation / propagation (X-Request-ID header)
  2. Structured log context setup (user_id, org_id, path, method)
  3. Prometheus HTTP metrics (latency, status code, in-flight)
  4. Sentry user context
  5. Request / response logging at INFO level

Add this middleware FIRST so it covers every other layer.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from cbms_api.observability.logging import set_request_context, clear_request_context
from cbms_api.observability.metrics import (
    http_requests_in_flight,
    normalize_path,
    record_http_request,
)
from cbms_api.observability.error_tracking import clear_sentry_user, set_sentry_user

logger = structlog.get_logger("cbms_api.request")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that instruments every HTTP request.

    Mount with::

        app.add_middleware(ObservabilityMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ------------------------------------------------------------------
        # 1. Request ID
        # ------------------------------------------------------------------
        request_id = (
            request.headers.get("X-Request-ID") or str(uuid.uuid4())
        )

        # ------------------------------------------------------------------
        # 2. Extract auth state (set by upstream auth middleware if present)
        # ------------------------------------------------------------------
        user = getattr(request.state, "user", None)
        user_id: str | None = str(user.user_id) if user else None
        org_id: str | None = str(user.org_id) if user else None
        email: str | None = getattr(user, "email", None) if user else None

        method = request.method
        path = request.url.path
        endpoint = normalize_path(path)

        # ------------------------------------------------------------------
        # 3. Bind structured-log context
        # ------------------------------------------------------------------
        set_request_context(
            request_id,
            user_id=user_id,
            org_id=org_id,
            path=path,
            method=method,
        )

        # ------------------------------------------------------------------
        # 4. Sentry user context
        # ------------------------------------------------------------------
        if user_id and org_id:
            set_sentry_user(user_id, org_id, email)

        # ------------------------------------------------------------------
        # 5. In-flight gauge
        # ------------------------------------------------------------------
        in_flight = http_requests_in_flight.labels(method=method, endpoint=endpoint)
        in_flight.inc()
        start = time.perf_counter()

        try:
            response: Response = await call_next(request)
            status = response.status_code
            duration = time.perf_counter() - start

            record_http_request(method, endpoint, status, duration)
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "request_completed",
                method=method,
                path=path,
                status_code=status,
                duration_ms=round(duration * 1000, 2),
            )
            return response

        except Exception as exc:
            duration = time.perf_counter() - start
            record_http_request(method, endpoint, 500, duration)
            logger.error(
                "request_failed",
                method=method,
                path=path,
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )
            raise

        finally:
            in_flight.dec()
            clear_request_context()
            clear_sentry_user()
