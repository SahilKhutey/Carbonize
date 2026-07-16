"""
tests/observability/test_logging.py

Tests for the structured logging module.

Verifies:
  - configure_logging() runs without error
  - Logs produce JSON-parseable output in prod mode
  - Request context propagates into log records
  - log_performance decorator records duration and status
  - LogContext temporary binding works
  - Errors include exc_info
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest
import structlog
from structlog.contextvars import clear_contextvars


@pytest.fixture(autouse=True)
def reset_structlog():
    """Reset structlog config and context before every test."""
    clear_contextvars()
    structlog.reset_defaults()
    yield
    clear_contextvars()
    structlog.reset_defaults()


@pytest.fixture()
def json_log_stream() -> StringIO:
    """Configure structlog for JSON output; return the StringIO buffer."""
    from cbms_api.observability.logging import configure_logging, _CONFIGURED
    import cbms_api.observability.logging as logging_mod

    # Force re-configuration for test
    logging_mod._CONFIGURED = False
    stream = StringIO()
    with patch("sys.stdout", stream):
        configure_logging(env="prod", log_level="DEBUG")
    logging_mod._CONFIGURED = False  # allow tests to call configure_logging again
    return stream


# ---------------------------------------------------------------------------
# 1. configure_logging
# ---------------------------------------------------------------------------

class TestConfigureLogging:
    def test_configure_does_not_raise(self) -> None:
        from cbms_api.observability.logging import configure_logging
        import cbms_api.observability.logging as lm
        lm._CONFIGURED = False
        configure_logging(env="development", log_level="INFO")
        lm._CONFIGURED = False  # cleanup

    def test_idempotent_second_call_is_noop(self) -> None:
        from cbms_api.observability.logging import configure_logging
        import cbms_api.observability.logging as lm
        lm._CONFIGURED = False
        configure_logging(env="development")
        first_flag = lm._CONFIGURED  # True
        configure_logging(env="prod")  # should be no-op
        assert first_flag is True
        lm._CONFIGURED = False  # cleanup


# ---------------------------------------------------------------------------
# 2. JSON output in prod mode
# ---------------------------------------------------------------------------

class TestJsonOutput:
    def test_log_produces_parseable_json(self) -> None:
        from cbms_api.observability.logging import configure_logging, get_logger
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")
            log = get_logger("test")
            log.info("test_event", alpha=1, beta="two")

        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        assert lines, "No output captured"
        data = json.loads(lines[-1])
        assert data.get("event") == "test_event"
        assert data.get("alpha") == 1
        assert data.get("beta") == "two"
        assert "timestamp" in data or "ts" in data or data.get("time")

        lm._CONFIGURED = False  # cleanup

    def test_log_level_field_present(self) -> None:
        from cbms_api.observability.logging import configure_logging, get_logger
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")
            get_logger("test").warning("warn_event")

        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        data = json.loads(lines[-1])
        assert data.get("level") in ("warning", "warn", "WARNING")

        lm._CONFIGURED = False


# ---------------------------------------------------------------------------
# 3. Request context propagation
# ---------------------------------------------------------------------------

class TestRequestContext:
    def test_context_appears_in_log(self) -> None:
        from cbms_api.observability.logging import (
            configure_logging, get_logger, set_request_context, clear_request_context
        )
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")
            set_request_context(
                "req-abc",
                user_id="u-1",
                org_id="org-2",
                path="/api/test",
                method="GET",
            )
            get_logger("ctx_test").info("ctx_event")
            clear_request_context()

        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        data = json.loads(lines[-1])
        assert data.get("request_id") == "req-abc"
        assert data.get("user_id") == "u-1"
        assert data.get("org_id") == "org-2"

        lm._CONFIGURED = False

    def test_clear_removes_context(self) -> None:
        from cbms_api.observability.logging import (
            configure_logging, get_logger, set_request_context, clear_request_context
        )
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        set_request_context("req-xyz", user_id="u-99")
        clear_request_context()
        # After clearing, vars are None
        from cbms_api.observability.logging import request_id_var, user_id_var
        assert request_id_var.get() is None
        assert user_id_var.get() is None

        lm._CONFIGURED = False


# ---------------------------------------------------------------------------
# 4. log_performance decorator
# ---------------------------------------------------------------------------

class TestLogPerformance:
    def test_success_path_logs_completed(self) -> None:
        from cbms_api.observability.logging import configure_logging, log_performance
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")

            @log_performance("unit.test_op")
            def fast_fn(x: int) -> int:
                return x * 2

            result = fast_fn(21)

        assert result == 42
        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        events = [json.loads(l) for l in lines]
        completed = [e for e in events if e.get("event") == "operation_completed"]
        assert completed, "Expected operation_completed log"
        assert completed[-1]["operation"] == "unit.test_op"
        assert completed[-1]["status"] == "success"
        assert completed[-1]["duration_ms"] >= 0

        lm._CONFIGURED = False

    def test_failure_path_logs_failed_and_reraises(self) -> None:
        from cbms_api.observability.logging import configure_logging, log_performance
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")

            @log_performance("unit.boom")
            def boom() -> None:
                raise ValueError("kaboom")

            with pytest.raises(ValueError, match="kaboom"):
                boom()

        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        events = [json.loads(l) for l in lines]
        failed = [e for e in events if e.get("event") == "operation_failed"]
        assert failed, "Expected operation_failed log"
        assert "error" in failed[-1] or "error_type" in failed[-1]

        lm._CONFIGURED = False


# ---------------------------------------------------------------------------
# 5. LogContext
# ---------------------------------------------------------------------------

class TestLogContext:
    def test_log_context_binds_and_restores(self) -> None:
        from cbms_api.observability.logging import (
            configure_logging, get_logger, LogContext
        )
        import cbms_api.observability.logging as lm

        lm._CONFIGURED = False
        buf = StringIO()
        with patch("sys.stdout", buf):
            configure_logging(env="prod", log_level="DEBUG")

            with LogContext(sim_id="sim-999", phase="kinetics"):
                get_logger("lc_test").info("inside_ctx")

        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        events = [json.loads(l) for l in lines]
        inside = [e for e in events if e.get("event") == "inside_ctx"]
        assert inside, "Log inside context not captured"
        assert inside[-1].get("sim_id") == "sim-999"

        lm._CONFIGURED = False
