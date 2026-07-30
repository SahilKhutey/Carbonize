"""
Apache Flink stream processing jobs for tumbling/sliding windows, CEP, and anomaly detection.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WindowedAggregator:
    """Computes streaming window aggregations over telemetry metrics."""
    
    def __init__(self, metric_type: str = "co2_ppm", window_seconds: int = 60):
        self.metric_type = metric_type
        self.window_seconds = window_seconds
    
    def process_window(self, elements: list) -> Dict[str, Any]:
        values = [e['value'] for e in elements if 'value' in e]
        if not values:
            return {}
        
        now = int(datetime.utcnow().timestamp() * 1000)
        return {
            'window_start': now - self.window_seconds * 1000,
            'window_end': now,
            'window_type': 'tumbling',
            'metric_type': self.metric_type,
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
        }


class StreamingAnomalyDetector:
    """Detects z-score anomalies over rolling stream windows."""
    
    def __init__(self, z_threshold: float = 3.0, window_size: int = 100):
        self.z_threshold = z_threshold
        self.window_size = window_size
        self._history = []
    
    def evaluate(self, value: float) -> Dict[str, Any]:
        self._history.append(value)
        if len(self._history) > self.window_size:
            self._history.pop(0)
            
        if len(self._history) < 10:
            return {'is_anomaly': False, 'z_score': 0.0}
            
        mean = sum(self._history) / len(self._history)
        variance = sum((x - mean) ** 2 for x in self._history) / len(self._history)
        std = variance ** 0.5 if variance > 0 else 1.0
        
        z_score = (value - mean) / std
        is_anomaly = abs(z_score) >= self.z_threshold
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': z_score,
            'mean': mean,
            'std': std,
            'severity': 'high' if abs(z_score) > 4.5 else 'medium' if is_anomaly else 'none',
        }


class PatternMatcherCEP:
    """Complex Event Processing pattern engine."""
    
    def __init__(self):
        self.detections = []
    
    def match(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get('class_name') == 'co2_emitter':
            self.detections.append(event)
            if len(self.detections) >= 3:
                pattern_event = {
                    'event_id': f"cep_{event.get('event_id')}",
                    'pattern': 'leak_suspected',
                    'severity': 'critical',
                    'count': len(self.detections),
                }
                self.detections.clear()
                return pattern_event
        return None
