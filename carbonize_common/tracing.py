"""
Distributed Tracing for Carbonize Pipeline
Fixes Bottleneck B23: No tracing across services
"""

import os
import time
import logging
import json
import uuid
from contextlib import contextmanager
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class SpanKind(Enum):
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


@dataclass
class TraceContext:
    """W3C trace context for cross-service propagation."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    flags: str = "01"
    
    def to_dict(self) -> Dict:
        return {
            "traceparent": f"00-{self.trace_id}-{self.span_id}-{self.flags}"
        }


@dataclass
class Span:
    """Individual span in a trace."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    kind: SpanKind
    start_time_ns: int
    end_time_ns: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: list = field(default_factory=list)
    status: str = "OK"
    status_message: str = ""
    
    @property
    def duration_ms(self) -> float:
        return (self.end_time_ns - self.start_time_ns) / 1e6
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "kind": self.kind.value,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": self.events,
            "status": self.status,
            "status_message": self.status_message
        }


class TracingManager:
    """Distributed tracing manager."""
    
    def __init__(self, service_name: str = "carbonize",
                 exporter_endpoint: Optional[str] = None):
        self.service_name = service_name
        self.exporter_endpoint = exporter_endpoint or os.getenv("OTEL_EXPORTER")
        self._active_spans: Dict[str, Span] = {}
        self._lock = threading.Lock()
        self._logs: list = []
        self._max_logs = 10000
    
    @contextmanager
    def span(self, name: str, kind: SpanKind = SpanKind.INTERNAL,
             parent: Optional[TraceContext] = None,
             attributes: Optional[Dict] = None):
        """Context manager for span creation."""
        if parent:
            trace_id = parent.trace_id
            parent_span_id = parent.span_id
        else:
            trace_id = uuid.uuid4().hex
            parent_span_id = None
        
        span_id = uuid.uuid4().hex[:16]
        
        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            kind=kind,
            start_time_ns=time.time_ns(),
            attributes=attributes or {}
        )
        
        with self._lock:
            self._active_spans[span_id] = span
        
        try:
            yield span
            span.status = "OK"
        except Exception as e:
            span.status = "ERROR"
            span.status_message = str(e)
            span.events.append({
                "name": "exception",
                "timestamp_ns": time.time_ns(),
                "attributes": {"exception.type": type(e).__name__,
                              "exception.message": str(e)}
            })
            raise
        finally:
            span.end_time_ns = time.time_ns()
            with self._lock:
                self._active_spans.pop(span_id, None)
            self._record_span(span)
    
    def _record_span(self, span: Span):
        """Record span to logs and optionally export."""
        log_entry = {
            "timestamp": time.time(),
            "service": self.service_name,
            **span.to_dict()
        }
        
        with self._lock:
            self._logs.append(log_entry)
            if len(self._logs) > self._max_logs:
                self._logs = self._logs[-self._max_logs:]
        
        logger = logging.getLogger(f"trace.{self.service_name}")
        logger.info(json.dumps(log_entry))
        
        if self.exporter_endpoint:
            self._export_span(span)
    
    def _export_span(self, span: Span):
        """Export span to OTLP endpoint (async)."""
        try:
            import requests
            requests.post(
                f"{self.exporter_endpoint}/v1/traces",
                json={
                    "resource_spans": [{
                        "resource": {"attributes": [
                            {"key": "service.name", "value": {"stringValue": self.service_name}}
                        ]},
                        "scope_spans": [{
                            "scope": {"name": self.service_name},
                            "spans": [{
                                "trace_id": span.trace_id,
                                "span_id": span.span_id,
                                "parent_span_id": span.parent_span_id or "",
                                "name": span.name,
                                "kind": span.kind.value,
                                "start_time_unix_nano": str(span.start_time_ns),
                                "end_time_unix_nano": str(span.end_time_ns),
                                "attributes": [
                                    {"key": k, "value": {"stringValue": str(v)}}
                                    for k, v in span.attributes.items()
                                ],
                                "status": {"code": 1 if span.status == "OK" else 2}
                            }]
                        }]
                    }]
                },
                timeout=0.5
            )
        except Exception:
            pass
    
    def inject_context(self, msg: dict) -> dict:
        """Inject trace context into outgoing message."""
        with self._lock:
            if self._active_spans:
                span = next(iter(self._active_spans.values()))
                msg['_trace'] = {
                    'trace_id': span.trace_id,
                    'span_id': span.span_id,
                    'flags': '01'
                }
        return msg
    
    def extract_context(self, msg: dict) -> Optional[TraceContext]:
        """Extract trace context from incoming message."""
        ctx = msg.get('_trace')
        if not ctx:
            return None
        return TraceContext(
            trace_id=ctx['trace_id'],
            span_id=ctx['span_id'],
            parent_span_id=ctx['span_id'],
            flags=ctx.get('flags', '01')
        )
    
    def get_recent_logs(self, n: int = 100) -> list:
        """Get recent logs for inspection."""
        with self._lock:
            return self._logs[-n:]


# Singleton instance
tracer = TracingManager()
