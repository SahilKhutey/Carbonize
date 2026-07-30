"""
NOx removal (SCR & SNCR)
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class SCRResult:
    NO_in: float
    NO_out: float
    NOx_in: float
    NOx_out: float
    NH3_injection_rate: float
    ammonia_slip: float
    conversion: float
    pressure_drop: float
    catalyst_age_factor: float


class SCR_System:
    """Selective Catalytic Reduction (SCR) system."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.space_velocity = self.config.get('space_velocity', 5000)
        self.NH3_NO_ratio = self.config.get('NH3_NO_ratio', 1.0)
    
    def calculate_performance(self, gas_flow_nm3_h: float, NO_in_ppm: float, NO2_in_ppm: float = 0.0) -> SCRResult:
        NOx_in = NO_in_ppm + NO2_in_ppm
        conversion = 92.5
        NOx_out = NOx_in * (1.0 - conversion / 100.0)
        NO_out = NO_in_ppm * (1.0 - conversion / 100.0)
        
        return SCRResult(
            NO_in=NO_in_ppm,
            NO_out=NO_out,
            NOx_in=NOx_in,
            NOx_out=NOx_out,
            NH3_injection_rate=self.NH3_NO_ratio,
            ammonia_slip=2.1,
            conversion=conversion,
            pressure_drop=1450.0,
            catalyst_age_factor=0.95,
        )


class SNCR_System:
    """Selective Non-Catalytic Reduction (SNCR) system."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def calculate_performance(self, NO_in_ppm: float) -> Dict:
        eff = 65.0
        NO_out = NO_in_ppm * (1.0 - eff / 100.0)
        return {
            'NO_in': NO_in_ppm,
            'NO_out': NO_out,
            'efficiency': eff,
            'NH3_slip': 12.5,
        }
