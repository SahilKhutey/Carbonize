"""
Pilot Plant Rig Simulation
"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RigSpec:
    name: str
    capacity_kg_h: float
    absorber_diameter: float = 0.1
    absorber_height: float = 2.0
    stripper_diameter: float = 0.08
    stripper_height: float = 1.5
    max_T: float = 423.0
    max_P: float = 500000.0


@dataclass
class RigOperatingPoint:
    flue_gas_flow: float = 10.0
    flue_gas_CO2: float = 0.12
    flue_gas_T: float = 313.15
    lean_solvent_flow: float = 0.5
    lean_solvent_loading: float = 0.20
    lean_solvent_T: float = 313.15
    stripper_T: float = 393.15
    stripper_P: float = 180000.0


class PilotRig:
    def __init__(self, spec: RigSpec):
        self.spec = spec
        self.op = RigOperatingPoint()

    def set_operating_point(self, op: RigOperatingPoint):
        if op.flue_gas_T > self.spec.max_T:
            raise ValueError("Temperature exceeds limit")
        self.op = op

    def capture_run(self, duration_min: float = 60.0, sample_interval_min: float = 5.0) -> List[Dict]:
        n_samples = max(1, int(duration_min / sample_interval_min))
        results = []
        for i in range(n_samples):
            capture_rate = 0.88 + np.random.uniform(-0.02, 0.02)
            results.append({
                'timestamp': i * sample_interval_min * 60,
                'flue_gas_flow': self.op.flue_gas_flow,
                'flue_gas_CO2_in': self.op.flue_gas_CO2,
                'vent_CO2': self.op.flue_gas_CO2 * (1 - capture_rate),
                'CO2_capture_efficiency': float(capture_rate * 100.0),
                'lean_loading': self.op.lean_solvent_loading,
                'rich_loading': float(self.op.lean_solvent_loading + capture_rate * 0.35),
                'reboiler_duty_kW': float(self.op.flue_gas_flow * capture_rate * 45.0),
            })
        return results
