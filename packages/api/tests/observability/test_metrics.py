"""
tests/observability/test_metrics.py

Tests for Prometheus metrics definitions and helper functions.

Verifies:
  - All expected metric families are registered in REGISTRY
  - normalize_path() replaces UUIDs and numeric IDs correctly
  - record_http_request() increments counters and histogram
  - record_simulation_submitted() increments correct counter
  - record_simulation_completed() increments counters and histogram
  - record_celery_task() increments correct labels
  - n_samples bucketing logic (1k / 10k / 50k+)
"""

from __future__ import annotations

import pytest
from prometheus_client import REGISTRY

# Force import so all metric objects are registered before any test runs
import cbms_api.observability.metrics  # noqa: F401


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _registered_names() -> set[str]:
    """Return all metric family names currently in the default REGISTRY."""
    return {m.name for m in REGISTRY.collect()}


def _metric_sample_sum(family_name: str, label_filter: dict) -> float:
    """Sum all sample values for a family where labels match."""
    total = 0.0
    for m in REGISTRY.collect():
        if m.name == family_name:
            for s in m.samples:
                if all(s.labels.get(k) == v for k, v in label_filter.items()):
                    total += s.value
    return total


# ---------------------------------------------------------------------------
# 1. Metric families registered
# ---------------------------------------------------------------------------


class TestMetricObjects:
    # prometheus_client stores Counter families under the base name (no _total suffix)
    COUNTER_BASES = [
        "cbms_http_requests",
        "cbms_http_request_errors",
        "cbms_auth_login",
        "cbms_auth_token_refresh",
        "cbms_simulations_submitted",
        "cbms_simulations_completed",
        "cbms_celery_tasks",
        "cbms_celery_task_retries",
        "cbms_ccts_credits_generated",
        "cbms_ccts_claims_submitted",
        "cbms_rate_limit_hits",
        "cbms_ws_messages",
        "cbms_db_query_errors",
    ]
    HISTOGRAM_BASES = [
        "cbms_http_request_duration_seconds",
        "cbms_simulation_duration_seconds",
        "cbms_celery_task_duration_seconds",
        "cbms_db_query_duration_seconds",
        "cbms_capture_efficiency_pct",
        "cbms_npv_at_completion_inr",
        "cbms_payback_months_at_completion",
    ]
    GAUGE_NAMES = [
        "cbms_http_requests_in_flight",
        "cbms_auth_active_sessions",
        "cbms_simulations_active",
        "cbms_celery_queue_depth",
        "cbms_celery_active_workers",
        "cbms_celery_stuck_tasks",
        "cbms_ws_active_connections",
        "cbms_tenants_active",
        "cbms_system_cpu_percent",
        "cbms_system_memory_used_bytes",
        "cbms_system_memory_total_bytes",
    ]

    @pytest.mark.parametrize("base", COUNTER_BASES)
    def test_counter_registered(self, base: str) -> None:
        names = _registered_names()
        assert base in names or f"{base}_total" in names, (
            f"Counter {base!r} not found. Registered: {sorted(n for n in names if 'cbms' in n)}"
        )

    @pytest.mark.parametrize("base", HISTOGRAM_BASES)
    def test_histogram_registered(self, base: str) -> None:
        names = _registered_names()
        assert f"{base}_count" in names or base in names, (
            f"Histogram {base!r} not found. Registered: {sorted(n for n in names if 'cbms' in n)}"
        )

    @pytest.mark.parametrize("name", GAUGE_NAMES)
    def test_gauge_registered(self, name: str) -> None:
        names = _registered_names()
        assert name in names, (
            f"Gauge {name!r} not found. Registered: {sorted(n for n in names if 'cbms' in n)}"
        )


# ---------------------------------------------------------------------------
# 2. normalize_path
# ---------------------------------------------------------------------------


class TestNormalizePath:
    def test_uuid_replaced(self) -> None:
        from cbms_api.observability.metrics import normalize_path
        path = "/api/v1/simulations/3f6c4b1a-1234-5678-abcd-000000000001"
        assert normalize_path(path) == "/api/v1/simulations/{id}"

    def test_numeric_id_replaced(self) -> None:
        from cbms_api.observability.metrics import normalize_path
        assert normalize_path("/api/v1/reports/42") == "/api/v1/reports/{id}"

    def test_multiple_ids_replaced(self) -> None:
        from cbms_api.observability.metrics import normalize_path
        path = "/org/3f6c4b1a-1234-5678-abcd-000000000001/simulations/99"
        result = normalize_path(path)
        assert "{id}" in result
        assert "3f6c4b1a" not in result
        assert "/99" not in result

    def test_clean_path_unchanged(self) -> None:
        from cbms_api.observability.metrics import normalize_path
        assert normalize_path("/api/v1/health") == "/api/v1/health"

    def test_case_insensitive_uuid(self) -> None:
        from cbms_api.observability.metrics import normalize_path
        path = "/items/3F6C4B1A-1234-5678-ABCD-000000000001"
        assert normalize_path(path) == "/items/{id}"


# ---------------------------------------------------------------------------
# 3. record_http_request
# ---------------------------------------------------------------------------


class TestRecordHttpRequest:
    def test_increments_requests_total(self) -> None:
        from cbms_api.observability.metrics import record_http_request, http_requests_total

        counter = http_requests_total.labels(method="GET", endpoint="/rhr-a", status="200")
        before = counter._value.get()
        record_http_request("GET", "/rhr-a", 200, 0.042)
        assert counter._value.get() == before + 1

    def test_4xx_increments_error_counter(self) -> None:
        from cbms_api.observability.metrics import record_http_request, http_request_errors_total

        counter = http_request_errors_total.labels(
            method="POST", endpoint="/rhr-login", status="401", error_class="4xx"
        )
        before = counter._value.get()
        record_http_request("POST", "/rhr-login", 401, 0.005)
        assert counter._value.get() == before + 1

    def test_5xx_increments_error_counter(self) -> None:
        from cbms_api.observability.metrics import record_http_request, http_request_errors_total

        counter = http_request_errors_total.labels(
            method="GET", endpoint="/rhr-crash", status="500", error_class="5xx"
        )
        before = counter._value.get()
        record_http_request("GET", "/rhr-crash", 500, 0.1)
        assert counter._value.get() == before + 1

    def test_2xx_does_not_increment_error_counter(self) -> None:
        from cbms_api.observability.metrics import record_http_request

        before = _metric_sample_sum("cbms_http_request_errors", {"endpoint": "/rhr-ok200"})
        record_http_request("GET", "/rhr-ok200", 200, 0.01)
        after = _metric_sample_sum("cbms_http_request_errors", {"endpoint": "/rhr-ok200"})
        assert before == after, "2xx should not touch error counter"

    def test_duration_histogram_observed(self) -> None:
        from cbms_api.observability.metrics import record_http_request, http_request_duration_seconds

        hist = http_request_duration_seconds.labels(method="PUT", endpoint="/rhr-upload")
        before = hist._sum.get()
        record_http_request("PUT", "/rhr-upload", 200, 1.234)
        assert hist._sum.get() == pytest.approx(before + 1.234, rel=1e-3)


# ---------------------------------------------------------------------------
# 4. Simulation helpers
# ---------------------------------------------------------------------------


class TestSimulationHelpers:
    def test_record_simulation_submitted(self) -> None:
        from cbms_api.observability.metrics import record_simulation_submitted, simulations_submitted_total

        counter = simulations_submitted_total.labels(org_id="org-sim-test", simulation_type="mc")
        before = counter._value.get()
        record_simulation_submitted("org-sim-test", "mc")
        assert counter._value.get() == before + 1

    def test_record_simulation_completed_success(self) -> None:
        from cbms_api.observability.metrics import record_simulation_completed, simulations_completed_total

        counter = simulations_completed_total.labels(org_id="org-sim-test2", status="success")
        before = counter._value.get()
        record_simulation_completed("org-sim-test2", "success", 45.0, "mc", 5_000)
        assert counter._value.get() == before + 1

    @pytest.mark.parametrize("n_samples,expected_bucket", [
        (100,    "1k"),
        (1_000,  "1k"),
        (5_000,  "10k"),
        (10_000, "10k"),
        (10_001, "50k+"),
        (50_000, "50k+"),
    ])
    def test_n_samples_bucketing(self, n_samples: int, expected_bucket: str) -> None:
        from cbms_api.observability.metrics import record_simulation_completed, simulation_duration_seconds

        hist = simulation_duration_seconds.labels(
            simulation_type="mc", n_samples_bucket=expected_bucket
        )
        before = hist._sum.get()
        record_simulation_completed("org-bucket-test", "success", 10.0, "mc", n_samples)
        assert hist._sum.get() == pytest.approx(before + 10.0, rel=1e-3)


# ---------------------------------------------------------------------------
# 5. Celery helper
# ---------------------------------------------------------------------------


class TestCeleryHelper:
    def test_record_celery_task_increments_counter(self) -> None:
        from cbms_api.observability.metrics import record_celery_task, celery_tasks_total

        counter = celery_tasks_total.labels(
            task_name="workers.report-test", queue="reporting", status="success"
        )
        before = counter._value.get()
        record_celery_task("workers.report-test", "reporting", "success", 12.5)
        assert counter._value.get() == before + 1

    def test_record_celery_task_records_duration(self) -> None:
        from cbms_api.observability.metrics import record_celery_task, celery_task_duration_seconds

        hist = celery_task_duration_seconds.labels(
            task_name="workers.sim-test", queue="compute_heavy"
        )
        before = hist._sum.get()
        record_celery_task("workers.sim-test", "compute_heavy", "failure", 5.5)
        assert hist._sum.get() == pytest.approx(before + 5.5, rel=1e-3)
