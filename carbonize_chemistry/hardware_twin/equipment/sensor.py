"""
Sensor model with noise, drift, and bias
"""
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class SensorModel:
    sensor_type: str
    units: str
    range_: Tuple[float, float]
    noise_sigma: float = 0.01
    bias: float = 0.0
    drift_rate: float = 0.0
    response_time: float = 1.0
    failure_mode: str = 'normal'
    
    true_value: float = 0.0
    last_reading: float = 0.0
    
    def read(self, true_val: Optional[float] = None) -> float:
        if true_val is not None:
            self.true_value = true_val
            
        if self.failure_mode == 'stuck':
            return self.last_reading
            
        noise = np.random.normal(0, self.noise_sigma * (abs(self.true_value) + 1.0))
        measured = self.true_value + self.bias + noise
        self.last_reading = max(self.range_[0], min(self.range_[1], float(measured)))
        return self.last_reading
    
    def update(self, dt: float):
        pass
