"""
Avro schemas for Kafka topics
Registered with Confluent Schema Registry
"""
from dataclasses import dataclass
from typing import Dict, Any

TELEMETRY_SCHEMA = {
    "type": "record",
    "name": "Telemetry",
    "namespace": "com.carbonize.streaming",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "robot_id", "type": "string"},
        {"name": "metric_type", "type": "string"},
        {"name": "value", "type": "double"},
        {"name": "unit", "type": ["null", "string"], "default": None},
        {"name": "position", "type": ["null", {
            "type": "record",
            "name": "Position",
            "fields": [
                {"name": "x", "type": "double"},
                {"name": "y", "type": "double"},
                {"name": "z", "type": "double"},
            ]
        }], "default": None},
        {"name": "metadata", "type": ["null", "string"], "default": None},
        {"name": "source", "type": "string"},
        {"name": "schema_version", "type": "int", "default": 1},
    ]
}

DETECTION_SCHEMA = {
    "type": "record",
    "name": "Detection",
    "namespace": "com.carbonize.streaming",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "robot_id", "type": "string"},
        {"name": "model_version", "type": "string"},
        {"name": "class_name", "type": "string"},
        {"name": "class_id", "type": "int"},
        {"name": "confidence", "type": "double"},
        {"name": "bbox", "type": {
            "type": "record",
            "name": "BBox",
            "fields": [
                {"name": "x_min", "type": "double"},
                {"name": "y_min", "type": "double"},
                {"name": "x_max", "type": "double"},
                {"name": "y_max", "type": "double"},
            ]
        }},
        {"name": "image_url", "type": ["null", "string"], "default": None},
        {"name": "inference_time_ms", "type": "double"},
        {"name": "position", "type": ["null", "Position"], "default": None},
        {"name": "schema_version", "type": "int", "default": 1},
    ]
}

ALERT_SCHEMA = {
    "type": "record",
    "name": "Alert",
    "namespace": "com.carbonize.streaming",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "alert_type", "type": "string"},
        {"name": "severity", "type": "string"},
        {"name": "message", "type": "string"},
        {"name": "source_id", "type": ["null", "string"], "default": None},
        {"name": "context", "type": ["null", "string"], "default": None},
        {"name": "schema_version", "type": "int", "default": 1},
    ]
}

AGGREGATE_SCHEMA = {
    "type": "record",
    "name": "Aggregate",
    "namespace": "com.carbonize.streaming",
    "fields": [
        {"name": "window_start", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "window_end", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "window_type", "type": "string"},
        {"name": "metric_type", "type": "string"},
        {"name": "group_by", "type": ["null", "string"], "default": None},
        {"name": "count", "type": "long"},
        {"name": "sum", "type": "double"},
        {"name": "avg", "type": "double"},
        {"name": "min", "type": "double"},
        {"name": "max", "type": "double"},
        {"name": "std", "type": ["null", "double"], "default": None},
        {"name": "p50", "type": ["null", "double"], "default": None},
        {"name": "p95", "type": ["null", "double"], "default": None},
        {"name": "p99", "type": ["null", "double"], "default": None},
        {"name": "schema_version", "type": "int", "default": 1},
    ]
}

SCHEMA_REGISTRY = {
    'telemetry': TELEMETRY_SCHEMA,
    'detection': DETECTION_SCHEMA,
    'alert': ALERT_SCHEMA,
    'aggregate': AGGREGATE_SCHEMA,
}
