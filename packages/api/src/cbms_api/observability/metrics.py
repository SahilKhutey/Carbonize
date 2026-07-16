"""
cbms_api/observability/metrics.py

Prometheus metrics definitions — all metric objects live here.

Categories
----------
HTTP       : RED pattern — Rate, Errors, Duration
Auth       : login, refresh, sessions
Business   : simulations, CCTS credits, NPV/payback distributions
Celery     : queue depth, task lifecycle, stuck tasks, rate-limit hits
Database   : query duration, pool state
WebSocket  : connection count, message traffic
System     : CPU, memory (updated via update_system_metrics())

Helpers
-------
record_http_request()          — call from ObservabilityMiddleware
record_simulation_submitted()  — call when Celery task enqueued
record_simulation_completed()  — call when Celery task finishes
record_celery_task()           — call from worker signals
update_system_metrics()        — call from periodic Celery beat task
"""

from __future__ import annotations

import re
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    REGISTRY as _DEFAULT_REGISTRY,
)

# Use the default registry so /metrics picks it up automatically
REGISTRY = _DEFAULT_REGISTRY

# ---------------------------------------------------------------------------
# HTTP  (RED)
# ---------------------------------------------------------------------------

http_requests_total = Counter(
    "cbms_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "cbms_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_request_errors_total = Counter(
    "cbms_http_request_errors_total",
    "Total HTTP request errors (4xx / 5xx)",
    ["method", "endpoint", "status", "error_class"],
)

http_requests_in_flight = Gauge(
    "cbms_http_requests_in_flight",
    "HTTP requests currently in flight",
    ["method", "endpoint"],
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

auth_login_total = Counter(
    "cbms_auth_login_total",
    "Total login attempts",
    ["status"],          # success | failure
)

auth_token_refresh_total = Counter(
    "cbms_auth_token_refresh_total",
    "Total token refresh attempts",
    ["status"],          # success | failure | expired
)

auth_active_sessions = Gauge(
    "cbms_auth_active_sessions",
    "Currently active authenticated sessions (refresh tokens in-store)",
)

auth_mfa_total = Counter(
    "cbms_auth_mfa_total",
    "MFA verification attempts",
    ["status"],          # success | failure
)

# ---------------------------------------------------------------------------
# Business KPIs
# ---------------------------------------------------------------------------

simulations_submitted_total = Counter(
    "cbms_simulations_submitted_total",
    "Total simulations submitted",
    ["org_id", "simulation_type"],
)

simulations_completed_total = Counter(
    "cbms_simulations_completed_total",
    "Total simulations completed",
    ["org_id", "status"],      # success | failed | timeout
)

simulation_duration_seconds = Histogram(
    "cbms_simulation_duration_seconds",
    "Simulation wall-clock duration in seconds",
    ["simulation_type", "n_samples_bucket"],   # n_samples_bucket: 1k | 10k | 50k+
    buckets=(5, 30, 60, 300, 600, 1800, 3600, 7200),
)

simulations_active = Gauge(
    "cbms_simulations_active",
    "Currently running simulations",
    ["simulation_type"],
)

capture_efficiency_distribution = Histogram(
    "cbms_capture_efficiency_pct",
    "Distribution of pollutant capture efficiency outcomes (%)",
    ["pollutant", "method"],    # pollutant: co2 | so2 | pm; method: mc | deterministic
    buckets=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100),
)

npv_at_completion = Histogram(
    "cbms_npv_at_completion_inr",
    "NPV at simulation completion (₹)",
    ["org_id"],
    buckets=(0, 1e6, 5e6, 1e7, 5e7, 1e8, 5e8, 1e9),
)

payback_months_at_completion = Histogram(
    "cbms_payback_months_at_completion",
    "Payback period at simulation completion (months)",
    ["org_id"],
    buckets=(6, 12, 18, 24, 36, 48, 60, 84, 120),
)

ccts_credits_generated_total = Counter(
    "cbms_ccts_credits_generated_total",
    "Cumulative CCTS credits generated",
    ["org_id", "fiscal_year"],
)

ccts_claims_submitted_total = Counter(
    "cbms_ccts_claims_submitted_total",
    "Total CCTS claims submitted to BEE",
    ["org_id", "status"],    # submitted | approved | rejected
)

tenants_active = Gauge(
    "cbms_tenants_active",
    "Tenants with activity in the last 7 days",
)

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

celery_tasks_total = Counter(
    "cbms_celery_tasks_total",
    "Total Celery tasks processed",
    ["task_name", "queue", "status"],   # status: success | failure | retry
)

celery_task_duration_seconds = Histogram(
    "cbms_celery_task_duration_seconds",
    "Celery task execution duration in seconds",
    ["task_name", "queue"],
    buckets=(1, 5, 10, 30, 60, 300, 600, 1800, 3600),
)

celery_queue_depth = Gauge(
    "cbms_celery_queue_depth",
    "Tasks currently waiting in a Celery queue",
    ["queue_name"],
)

celery_active_workers = Gauge(
    "cbms_celery_active_workers",
    "Active Celery worker processes",
    ["queue_name"],
)

celery_task_retries_total = Counter(
    "cbms_celery_task_retries_total",
    "Total Celery task retries due to transient failures",
    ["task_name", "queue"],
)

celery_stuck_tasks = Gauge(
    "cbms_celery_stuck_tasks",
    "Tasks stuck in GENERATING beyond timeout",
    ["queue_name", "task_name"],
)

celery_rate_limited_total = Counter(
    "cbms_celery_rate_limited_total",
    "Tasks rejected by the per-user rate limiter before enqueue",
    ["endpoint"],
)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

db_query_duration_seconds = Histogram(
    "cbms_db_query_duration_seconds",
    "Database query round-trip duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)

db_connection_pool = Gauge(
    "cbms_db_connection_pool",
    "Current DB connection pool size",
    ["state"],    # active | idle | overflow
)

db_query_errors_total = Counter(
    "cbms_db_query_errors_total",
    "Total database query errors",
    ["error_type"],
)

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

rate_limit_hits_total = Counter(
    "cbms_rate_limit_hits_total",
    "Requests rejected by rate limiting",
    ["endpoint", "tier"],    # tier: per_user | global
)

# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

ws_active_connections = Gauge(
    "cbms_ws_active_connections",
    "Active WebSocket connections",
    ["endpoint"],
)

ws_messages_total = Counter(
    "cbms_ws_messages_total",
    "Total WebSocket messages sent/received",
    ["direction", "msg_type"],   # direction: in | out
)

# ---------------------------------------------------------------------------
# System (updated periodically)
# ---------------------------------------------------------------------------

system_cpu_percent = Gauge("cbms_system_cpu_percent", "CPU usage (%)")
system_memory_used_bytes = Gauge("cbms_system_memory_used_bytes", "RAM used (bytes)")
system_memory_total_bytes = Gauge("cbms_system_memory_total_bytes", "Total RAM (bytes)")


def update_system_metrics() -> None:
    """Refresh system-level gauges. Call from a periodic Celery beat task."""
    try:
        import psutil  # soft dependency — not required in all envs
        system_cpu_percent.set(psutil.cpu_percent(interval=None))
        mem = psutil.virtual_memory()
        system_memory_used_bytes.set(mem.used)
        system_memory_total_bytes.set(mem.total)
    except ImportError:
        pass  # psutil not available in lightweight envs


# ---------------------------------------------------------------------------
# Convenience helpers called by middleware / services
# ---------------------------------------------------------------------------

_UUID_RE = re.compile(
    r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
_NUM_RE = re.compile(r"/\d+")


def normalize_path(path: str) -> str:
    """
    Replace UUIDs and numeric IDs in a URL path with ``{id}`` placeholder.

    Keeps metric cardinality low.

    Examples::

        /api/v1/simulations/abc123  → /api/v1/simulations/{id}
        /api/v1/reports/42          → /api/v1/reports/{id}
    """
    path = _UUID_RE.sub("/{id}", path)
    path = _NUM_RE.sub("/{id}", path)
    return path


def record_http_request(
    method: str,
    endpoint: str,
    status: int,
    duration: float,
) -> None:
    """Record all HTTP metrics for a single request."""
    http_requests_total.labels(
        method=method, endpoint=endpoint, status=str(status)
    ).inc()
    http_request_duration_seconds.labels(
        method=method, endpoint=endpoint
    ).observe(duration)
    if status >= 400:
        http_request_errors_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
            error_class="4xx" if status < 500 else "5xx",
        ).inc()


def record_simulation_submitted(org_id: str, sim_type: str) -> None:
    simulations_submitted_total.labels(
        org_id=org_id, simulation_type=sim_type
    ).inc()


def record_simulation_completed(
    org_id: str,
    status: str,
    duration_s: float,
    sim_type: str,
    n_samples: int,
) -> None:
    simulations_completed_total.labels(org_id=org_id, status=status).inc()
    bucket = (
        "1k" if n_samples <= 1_000
        else "10k" if n_samples <= 10_000
        else "50k+"
    )
    simulation_duration_seconds.labels(
        simulation_type=sim_type, n_samples_bucket=bucket
    ).observe(duration_s)


def record_celery_task(
    task_name: str,
    queue: str,
    status: str,
    duration_s: float,
) -> None:
    celery_tasks_total.labels(
        task_name=task_name, queue=queue, status=status
    ).inc()
    celery_task_duration_seconds.labels(
        task_name=task_name, queue=queue
    ).observe(duration_s)
