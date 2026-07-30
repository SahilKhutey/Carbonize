"""
Real-time drift detection on streaming data
Supports multiple detection methods with adaptive thresholds
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from scipy import stats
from scipy.spatial.distance import jensenshannon
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class DriftResult:
    method: str
    feature: str
    is_drifted: bool
    score: float
    threshold: float
    statistic: float
    p_value: Optional[float] = None
    confidence: float = 0.0
    timestamp: int = field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftSummary:
    timestamp: int
    overall_drifted: bool
    overall_score: float
    n_features_drifted: int
    n_features: int
    results: List[DriftResult]
    recommended_action: str
    confidence: float = 0.0


class DriftMethod(ABC):
    @abstractmethod
    def detect(self, reference: np.ndarray, test: np.ndarray, threshold: float = 0.05) -> DriftResult:
        pass


class KSTestDrift(DriftMethod):
    def detect(self, reference, test, threshold=0.05, **kwargs) -> DriftResult:
        statistic, p_value = stats.ks_2samp(reference, test)
        is_drifted = p_value < threshold
        return DriftResult(
            method='ks_test',
            feature=kwargs.get('feature', 'unknown'),
            is_drifted=is_drifted,
            score=1 - p_value,
            threshold=threshold,
            statistic=float(statistic),
            p_value=float(p_value),
            confidence=1 - p_value,
        )


class PSIDrift(DriftMethod):
    def detect(self, reference, test, threshold=0.25, n_bins=10, **kwargs) -> DriftResult:
        eps = 1e-10
        bins = np.linspace(min(reference.min(), test.min()) - eps, max(reference.max(), test.max()) + eps, n_bins + 1)
        ref_counts, _ = np.histogram(reference, bins=bins)
        test_counts, _ = np.histogram(test, bins=bins)
        
        ref_props = (ref_counts + eps) / (len(reference) + eps * n_bins)
        test_props = (test_counts + eps) / (len(test) + eps * n_bins)
        
        psi = float(np.sum((test_props - ref_props) * np.log(test_props / ref_props)))
        is_drifted = psi > threshold
        
        return DriftResult(
            method='psi',
            feature=kwargs.get('feature', 'unknown'),
            is_drifted=is_drifted,
            score=psi,
            threshold=threshold,
            statistic=psi,
            confidence=min(psi / threshold, 1.0),
        )


class JSDivergenceDrift(DriftMethod):
    def detect(self, reference, test, threshold=0.1, n_bins=20, **kwargs) -> DriftResult:
        eps = 1e-10
        bins = np.linspace(min(reference.min(), test.min()) - eps, max(reference.max(), test.max()) + eps, n_bins + 1)
        ref_hist, _ = np.histogram(reference, bins=bins)
        test_hist, _ = np.histogram(test, bins=bins)
        
        ref_p = (ref_hist + eps) / (ref_hist.sum() + eps * n_bins)
        test_p = (test_hist + eps) / (test_hist.sum() + eps * n_bins)
        
        js_div = float(jensenshannon(ref_p, test_p))
        is_drifted = js_div > threshold
        
        return DriftResult(
            method='js_divergence',
            feature=kwargs.get('feature', 'unknown'),
            is_drifted=is_drifted,
            score=js_div,
            threshold=threshold,
            statistic=js_div,
            confidence=min(js_div / threshold, 1.0),
        )


class MultiMethodDriftDetector:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'methods': ['ks_test', 'psi', 'js_divergence'],
            'thresholds': {'ks_test': 0.05, 'psi': 0.25, 'js_divergence': 0.1},
            'min_methods_drifted': 2,
            'min_samples': 30,
        }
        self.method_classes = {
            'ks_test': KSTestDrift,
            'psi': PSIDrift,
            'js_divergence': JSDivergenceDrift,
        }
    
    def detect(self, feature_data: Dict[str, np.ndarray], reference_data: Dict[str, np.ndarray], timestamp: int = None) -> DriftSummary:
        results = []
        n_drifted = 0
        
        for feature_name, test_data in feature_data.items():
            if feature_name not in reference_data:
                continue
            ref_data = reference_data[feature_name]
            if len(ref_data) < self.config['min_samples'] or len(test_data) < self.config['min_samples']:
                continue
            
            method_results = []
            for method_name in self.config['methods']:
                method = self.method_classes[method_name]()
                threshold = self.config['thresholds'].get(method_name, 0.05)
                res = method.detect(reference=ref_data, test=test_data, threshold=threshold, feature=feature_name)
                method_results.append(res)
            
            if method_results:
                n_methods_drifted = sum(1 for r in method_results if r.is_drifted)
                overall_drifted = n_methods_drifted >= self.config['min_methods_drifted']
                primary = max(method_results, key=lambda r: r.score)
                primary.is_drifted = overall_drifted
                results.append(primary)
                if overall_drifted:
                    n_drifted += 1
        
        overall_score = sum(r.score for r in results) / max(len(results), 1)
        overall_drifted = n_drifted > 0
        action = 'trigger_retraining' if n_drifted > len(results) / 2 else 'monitor' if overall_drifted else 'continue'
        
        return DriftSummary(
            timestamp=timestamp or int(datetime.utcnow().timestamp() * 1000),
            overall_drifted=overall_drifted,
            overall_score=overall_score,
            n_features_drifted=n_drifted,
            n_features=len(results),
            results=results,
            recommended_action=action,
        )


class StreamingDriftDetector:
    def __init__(self, metric_type: str, reference_window_size: int = 1000, test_window_size: int = 500, comparison_interval: int = 100):
        self.metric_type = metric_type
        self.reference_window_size = reference_window_size
        self.test_window_size = test_window_size
        self.comparison_interval = comparison_interval
        
        self._reference_buffer = deque(maxlen=reference_window_size)
        self._test_buffer = deque(maxlen=test_window_size)
        self.detector = MultiMethodDriftDetector()
        self._history = deque(maxlen=100)
    
    def add_value(self, value: float):
        self._test_buffer.append(float(value))
        if len(self._test_buffer) > 100:
            self._reference_buffer.append(float(value))
    
    def check_drift(self, force: bool = False) -> Optional[DriftSummary]:
        if len(self._test_buffer) < 30 or len(self._reference_buffer) < 30:
            return None
        
        ref_data = {'value': np.array(list(self._reference_buffer))}
        test_data = {'value': np.array(list(self._test_buffer))}
        
        summary = self.detector.detect(test_data, ref_data)
        self._history.append(summary)
        return summary
    
    def get_history(self, n: int = 100) -> List[DriftSummary]:
        return list(self._history)[-n:]
    
    def reset(self):
        self._reference_buffer.clear()
        self._test_buffer.clear()


class ConceptDriftDetector:
    def __init__(self, model_id: str, window_size: int = 500):
        self.model_id = model_id
        self.window_size = window_size
        self._errors = deque(maxlen=window_size)
    
    def record_prediction(self, prediction: Dict, ground_truth: Optional[Dict] = None):
        if ground_truth:
            err = 0.0 if prediction.get('class_name') == ground_truth.get('class_name') else 1.0
            self._errors.append(err)
    
    def check_drift(self) -> Dict[str, Any]:
        if len(self._errors) < 20:
            return {'drift_detected': False, 'current_error_rate': 0.0}
        
        err_rate = sum(self._errors) / len(self._errors)
        return {
            'drift_detected': err_rate > 0.25,
            'warning': err_rate > 0.15,
            'current_error_rate': err_rate,
            'severity': 'critical' if err_rate > 0.25 else 'normal',
        }
