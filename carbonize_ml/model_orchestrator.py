"""
Production Model Orchestrator with Graceful Degradation
Fixes Bottleneck B24: Hard failure on model issues
"""

import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from ultralytics import YOLO
import numpy as np
import cv2
import threading


class ModelState(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


@dataclass
class ModelHealthMetrics:
    """Health metrics for a model."""
    total_inferences: int = 0
    successful_inferences: int = 0
    failed_inferences: int = 0
    consecutive_failures: int = 0
    avg_latency_ms: float = 0.0
    last_failure_time: float = 0.0
    last_failure_reason: str = ""
    
    @property
    def success_rate(self) -> float:
        return self.successful_inferences / max(self.total_inferences, 1)
    
    @property
    def state(self) -> ModelState:
        if self.consecutive_failures >= 10:
            return ModelState.FAILED
        if self.success_rate < 0.8 or self.consecutive_failures >= 3:
            return ModelState.DEGRADED
        return ModelState.HEALTHY


class DetectorStrategy(ABC):
    """Abstract detection strategy."""
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Dict]:
        pass
    
    @abstractmethod
    def name(self) -> str:
        pass


class YOLODetector(DetectorStrategy):
    """Primary YOLO detector."""
    
    def __init__(self, model_path: str, device: str = 'cuda'):
        self.model = YOLO(model_path)
        self.device = device
        self._model_name = Path(model_path).stem
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        results = self.model.predict(frame, verbose=False, device=self.device)
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'class': self.model.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].cpu().numpy().tolist(),
                    'source': self._model_name
                })
        return detections
    
    def name(self) -> str:
        return f'yolo:{self._model_name}'


class EdgeTPUDetector(DetectorStrategy):
    """Edge TPU fallback (Coral)."""
    
    def __init__(self, model_path: str):
        try:
            from pycoral.utils import edgetpu
            from pycoral.adapters import common, detect
            self.interpreter = edgetpu.make_interpreter(model_path)
            self.interpreter.allocate_tensors()
            self._ready = True
        except Exception as e:
            logging.warning(f'EdgeTPU not available: {e}')
            self._ready = False
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        if not self._ready:
            raise RuntimeError("EdgeTPU not initialized")
        return []
    
    def name(self) -> str:
        return 'edge_tpu'


class ClassicalCVDetector(DetectorStrategy):
    """Classical CV fallback (no ML)."""
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        yellow_mask = cv2.inRange(hsv, (20, 100, 100), (30, 255, 255))
        orange_mask = cv2.inRange(hsv, (10, 100, 100), (20, 255, 255))
        combined = cv2.bitwise_or(yellow_mask, orange_mask)
        
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'class': 'industrial_marker',
                    'confidence': 0.5,
                    'bbox': [x, y, x+w, y+h],
                    'source': 'classical_cv'
                })
        return detections
    
    def name(self) -> str:
        return 'classical_cv'


class NoOpDetector(DetectorStrategy):
    """Last-resort no-op detector."""
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        return []
    
    def name(self) -> str:
        return 'noop'


class ModelOrchestrator:
    """
    Intelligent model orchestrator with hot-swap and fallback.
    
    Architecture:
        Request → Primary (YOLO-full)
                     ↓ (failure)
                Secondary (YOLO-nano)
                     ↓ (failure)
                Tertiary (EdgeTPU)
                     ↓ (failure)
                Classical CV
                     ↓ (failure)
                NoOp (with alert)
    """
    
    def __init__(self, primary_model_path: str = 'yolov8n.pt',
                 fallback_model_path: Optional[str] = None,
                 edgetpu_path: Optional[str] = None):
        self.logger = logging.getLogger('model-orchestrator')
        
        self.strategies: List[DetectorStrategy] = []
        self.strategies.append(YOLODetector(primary_model_path, device='cpu'))
        
        if fallback_model_path:
            self.strategies.append(YOLODetector(fallback_model_path, device='cpu'))
        
        if edgetpu_path:
            self.strategies.append(EdgeTPUDetector(edgetpu_path))
        
        self.strategies.append(ClassicalCVDetector())
        self.strategies.append(NoOpDetector())
        
        self.health: Dict[str, ModelHealthMetrics] = {
            s.name(): ModelHealthMetrics() for s in self.strategies
        }
        
        self.active_idx = 0
        self._lock = threading.Lock()
        self._alert_callbacks: List[Callable] = []
    
    def detect(self, frame: np.ndarray) -> Dict:
        """Run detection with automatic fallback."""
        last_error = None
        
        for i, strategy in enumerate(self.strategies):
            if i < self.active_idx:
                continue
            
            health = self.health[strategy.name()]
            
            if health.state == ModelState.FAILED:
                continue
            
            try:
                start = time.perf_counter()
                detections = strategy.detect(frame)
                elapsed_ms = (time.perf_counter() - start) * 1000
                
                health.total_inferences += 1
                health.successful_inferences += 1
                health.consecutive_failures = 0
                health.avg_latency_ms = (
                    0.9 * health.avg_latency_ms + 0.1 * elapsed_ms
                )
                
                if i > self.active_idx and health.state == ModelState.HEALTHY:
                    if health.successful_inferences >= 10:
                        self._promote_strategy(i)
                
                return {
                    'detections': detections,
                    'model_used': strategy.name(),
                    'model_state': health.state.value,
                    'latency_ms': elapsed_ms,
                    'degraded': i > 0
                }
                
            except Exception as e:
                self._handle_failure(strategy, e)
                last_error = e
                continue
        
        self._trigger_alert('all_models_failed', last_error)
        return {
            'detections': [],
            'model_used': 'none',
            'model_state': 'FAILED',
            'latency_ms': 0.0,
            'degraded': True,
            'error': str(last_error) if last_error else 'unknown'
        }
    
    def _handle_failure(self, strategy: DetectorStrategy, error: Exception):
        """Record failure and downgrade if needed."""
        health = self.health[strategy.name()]
        health.total_inferences += 1
        health.failed_inferences += 1
        health.consecutive_failures += 1
        health.last_failure_time = time.time()
        health.last_failure_reason = str(error)
        
        self.logger.warning(
            f'{strategy.name()} failed: {error} '
            f'(consecutive: {health.consecutive_failures})'
        )
        
        if health.state == ModelState.FAILED:
            self._demote_strategy(strategy)
    
    def _promote_strategy(self, idx: int):
        """Promote a healthier strategy back to active."""
        with self._lock:
            old = self.active_idx
            self.active_idx = idx
            self.logger.info(f'Promoted strategy: {self.strategies[idx].name()}')
            self._trigger_alert('strategy_promoted', {
                'from': self.strategies[old].name(),
                'to': self.strategies[idx].name()
            })
    
    def _demote_strategy(self, strategy: DetectorStrategy):
        """Demote a failed strategy."""
        with self._lock:
            current = self.strategies[self.active_idx]
            if current.name() == strategy.name():
                for i in range(self.active_idx + 1, len(self.strategies)):
                    h = self.health[self.strategies[i].name()]
                    if h.state != ModelState.FAILED:
                        self.active_idx = i
                        self.logger.warning(
                            f'Demoted to {self.strategies[i].name()} '
                            f'after {strategy.name()} failed'
                        )
                        self._trigger_alert('strategy_demoted', {
                            'from': strategy.name(),
                            'to': self.strategies[i].name()
                        })
                        return
    
    def get_status(self) -> Dict:
        """Get current orchestrator status."""
        return {
            'active_strategy': self.strategies[self.active_idx].name(),
            'strategies': [
                {
                    'name': s.name(),
                    'state': self.health[s.name()].state.value,
                    'success_rate': self.health[s.name()].success_rate,
                    'avg_latency_ms': self.health[s.name()].avg_latency_ms,
                    'consecutive_failures': self.health[s.name()].consecutive_failures
                }
                for s in self.strategies
            ]
        }
    
    def on_alert(self, callback: Callable):
        """Register alert callback."""
        self._alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, data):
        """Trigger alert to all listeners."""
        for cb in self._alert_callbacks:
            try:
                cb(alert_type, data)
            except Exception:
                pass
