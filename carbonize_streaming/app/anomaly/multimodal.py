"""
Multi-modal anomaly detection with correlation analysis
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import logging
import time


logger = logging.getLogger(__name__)


class MultiModalAnomalyDetector:
    """Combines multiple anomaly detection methods with correlation analysis."""
    
    def __init__(
        self,
        config: Optional[Dict] = None,
        correlation_window: int = 100,
        ensemble_method: str = 'weighted_max',
    ):
        self.config = config or {}
        self.correlation_window = correlation_window
        self.ensemble_method = ensemble_method
        
        self._histories: Dict[str, deque] = {}
        self._anomaly_events: Dict[str, deque] = {}
        self._correlation_matrix: Dict[Tuple[str, str], float] = {}
    
    def add_value(self, metric_type: str, value: float, 
                  source_id: Optional[str] = None) -> Optional[Dict]:
        """Add a value and return combined anomaly detection."""
        key = f"{metric_type}_{source_id}" if source_id else metric_type
        
        if key not in self._histories:
            self._histories[key] = deque(maxlen=self.correlation_window)
            self._anomaly_events[key] = deque(maxlen=100)
        
        self._histories[key].append(float(value))
        scores = self._compute_scores(key, value)
        
        if not scores:
            return None
        
        is_anomaly, confidence = self._ensemble_scores(scores)
        correlated = self._find_correlated_anomalies(key, value)
        
        event = {
            'timestamp': int(time.time() * 1000),
            'metric_type': metric_type,
            'source_id': source_id,
            'value': float(value),
            'scores': scores,
            'is_anomaly': is_anomaly,
            'severity': self._get_severity(confidence),
            'confidence': confidence,
            'correlated_anomalies': correlated,
        }
        
        if is_anomaly:
            self._anomaly_events[key].append(event)
        
        return event
    
    def _compute_scores(self, key: str, value: float) -> Dict[str, float]:
        """Compute anomaly scores from multiple methods."""
        scores = {}
        history = self._histories.get(key, deque())
        
        if len(history) < 5:
            return {'z_score': 0.1, 'iqr': 0.0, 'ma_deviation': 0.1}
        
        history_array = np.array(list(history))
        
        # Z-score
        mean = float(history_array.mean())
        std = float(history_array.std()) if history_array.std() > 0 else 1.0
        z_score = abs((value - mean) / std)
        scores['z_score'] = float(min(z_score / 5.0, 1.0))
        
        # Modified Z-score (using MAD)
        median = float(np.median(history_array))
        mad = float(np.median(np.abs(history_array - median)))
        if mad > 0:
            modified_z = 0.6745 * (value - median) / mad
            scores['modified_z'] = float(min(abs(modified_z) / 5.0, 1.0))
        else:
            scores['modified_z'] = 0.0
        
        # IQR-based
        q1, q3 = np.percentile(history_array, [25, 75])
        iqr = q3 - q1
        if iqr > 0:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            scores['iqr'] = 1.0 if (value < lower or value > upper) else 0.0
        else:
            scores['iqr'] = 0.0
        
        # Moving average deviation
        ma = float(history_array[-20:].mean()) if len(history_array) >= 20 else mean
        deviation = abs(value - ma) / (abs(ma) + 1e-10)
        scores['ma_deviation'] = float(min(deviation, 1.0))
        
        return scores
    
    def _ensemble_scores(self, scores: Dict[str, float]) -> Tuple[bool, float]:
        """Combine multiple scores into final anomaly decision."""
        if not scores:
            return False, 0.0
        
        score_values = list(scores.values())
        sorted_scores = sorted(score_values, reverse=True)
        weights = [0.4, 0.3, 0.2, 0.1][:len(sorted_scores)]
        confidence = float(
            sum(s * w for s, w in zip(sorted_scores, weights)) / sum(weights)
        )
        
        threshold = self.config.get('anomaly_threshold', 0.5)
        is_anomaly = confidence >= threshold
        
        return is_anomaly, confidence
    
    def _find_correlated_anomalies(self, current_key: str, current_value: float) -> List[str]:
        """Find correlated anomalies across metrics."""
        correlated = []
        if len(self._histories.get(current_key, deque())) < 10:
            return correlated
        
        current_history = np.array(list(self._histories[current_key]))
        for other_key, other_history in self._histories.items():
            if other_key == current_key or len(other_history) < 10:
                continue
            other_arr = np.array(list(other_history))
            min_len = min(len(current_history), len(other_arr))
            if min_len < 10:
                continue
            
            corr = np.corrcoef(current_history[-min_len:], other_arr[-min_len:])[0, 1]
            if not np.isnan(corr) and abs(corr) > 0.6:
                correlated.append(other_key)
        
        return correlated
    
    def _get_severity(self, confidence: float) -> str:
        if confidence >= 0.85:
            return 'critical'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        else:
            return 'low'
