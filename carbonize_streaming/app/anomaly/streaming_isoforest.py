"""
Streaming Isolation Forest using Half-Space Trees
"""
import numpy as np
from typing import List, Optional, Tuple, Dict
from collections import deque
import random
import logging
import time


logger = logging.getLogger(__name__)


class HalfSpaceTree:
    """Half-Space Tree for streaming isolation forest."""
    
    def __init__(self, height: int, bounds: Tuple[float, float]):
        self.height = height
        self.bounds = bounds
        self.left = None
        self.right = None
        self.mass = 0
        self.r = None
    
    def update(self, point: float, current_height: int = 0) -> float:
        """Update tree with a point and return anomaly score."""
        if current_height >= self.height:
            self.mass += 1
            return float(self.height)
        
        if self.r is None:
            self.r = random.uniform(self.bounds[0], self.bounds[1])
        
        if point < self.r:
            if self.left is None:
                self.left = HalfSpaceTree(self.height - 1, (self.bounds[0], self.r))
            score = self.left.update(point, current_height + 1)
        else:
            if self.right is None:
                self.right = HalfSpaceTree(self.height - 1, (self.r, self.bounds[1]))
            score = self.right.update(point, current_height + 1)
        
        self.mass += 1
        return score


class StreamingIsolationForest:
    """Streaming Isolation Forest using ensemble of Half-Space Trees."""
    
    def __init__(
        self,
        n_trees: int = 100,
        height: int = 8,
        window_size: int = 1000,
        bounds: Tuple[float, float] = (-1e6, 1e6),
        anomaly_threshold: float = 0.7,
    ):
        self.n_trees = n_trees
        self.height = height
        self.window_size = window_size
        self.bounds = bounds
        self.anomaly_threshold = anomaly_threshold
        
        self._trees = [HalfSpaceTree(self.height, bounds) for _ in range(n_trees)]
        self._window = deque(maxlen=window_size)
        self._scoring_window = deque(maxlen=window_size)
        
        self._c = self._compute_c(window_size)
    
    def add_sample(self, value: float) -> Dict:
        """Add a sample and detect anomaly."""
        self._window.append(float(value))
        
        scores = []
        for tree in self._trees:
            score = tree.update(float(value))
            scores.append(score)
        
        avg_score = float(np.mean(scores) / max(self._c, 1.0))
        self._scoring_window.append(avg_score)
        
        is_anomaly = avg_score > self.anomaly_threshold
        
        if len(self._scoring_window) > 100:
            adaptive_threshold = float(np.percentile(list(self._scoring_window), 95))
        else:
            adaptive_threshold = self.anomaly_threshold
        
        return {
            'value': float(value),
            'score': float(avg_score),
            'threshold': adaptive_threshold,
            'is_anomaly': bool(is_anomaly),
            'timestamp': int(time.time() * 1000),
        }
    
    def _compute_c(self, n: int) -> float:
        """Compute normalization constant c(n)."""
        if n <= 1:
            return 1.0
        import math
        h = math.log(n - 1) + 0.5772156649
        return 2.0 * h - (2.0 * (n - 1) / n)
    
    def reset(self):
        """Reset all trees."""
        self._trees = [HalfSpaceTree(self.height, self.bounds) for _ in range(self.n_trees)]
        self._window.clear()
        self._scoring_window.clear()
