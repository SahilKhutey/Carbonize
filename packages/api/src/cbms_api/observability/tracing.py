"""
cbms_api/observability/tracing.py

OpenTelemetry distributed tracing setup.

Produces W3C-format trace/span IDs that propagate across services
(FastAPI → Celery → DB).  Exports to an OTLP collector (e.g. Grafana Tempo).

Usage::

    from cbms_api.observability.tracing import setup_tracing
    setup_tracing(service_name="cbms-api", endpoint="http://tempo:4317")

All instrumentation is opt-in and gracefully no-ops if the
``opentelemetry-sdk`` package is not installed.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


def setup_tracing(
    service_name: str = "cbms-api",
    endpoint: str = "http://localhost:4317",
    *,
    enabled: bool = True,
) -> None:
    """
    Configure OpenTelemetry tracing.

    Args:
        service_name: Appears in Grafana Tempo / Jaeger as the service label.
        endpoint:     OTLP gRPC collector endpoint.
        enabled:      Set False to disable entirely (e.g. in test env).
    """
    if not enabled:
        logger.info("otel_tracing_disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        resource = Resource(attributes={"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()

        logger.info(
            "otel_tracing_initialized",
            service=service_name,
            endpoint=endpoint,
        )

    except ImportError as exc:
        logger.warning(
            "otel_tracing_unavailable",
            reason=str(exc),
            advice="pip install opentelemetry-sdk opentelemetry-exporter-otlp",
        )


def get_current_trace_id() -> str:
    """Return the active trace ID as a hex string (for log correlation)."""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.trace_id, "032x")
    except Exception:
        pass
    return ""
