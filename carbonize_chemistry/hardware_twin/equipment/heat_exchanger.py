"""
Heat exchanger model with fouling
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class HeatExchanger:
    duty_max: float = 50e6
    area: float = 2000.0
    U_clean: float = 1500.0
    fouling_factor: float = 0.0
    
    def update(
        self,
        hot_in_T: float,
        hot_out_T: float,
        cold_in_T: float,
        cold_out_T: float,
        hot_flow: float,
        cold_flow: float,
    ) -> float:
        Q = hot_flow * 4186.0 * abs(hot_in_T - hot_out_T)
        return float(min(self.duty_max, Q))
