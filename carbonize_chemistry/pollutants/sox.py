"""
SOx absorption in alkaline solutions
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class SOxRemovalResult:
    SO2_in: float
    SO2_out: float
    SO3_in: float
    SO3_out: float
    removal_efficiency: float
    limestone_consumed: float
    gypsum_produced: float
    wastewater_volume: float
    ph_drift: float


class WetLimestoneSOxScrubber:
    """Wet limestone FGD scrubber."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.slurry_pH = self.config.get('slurry_pH', 5.5)
        self.L_G_ratio = self.config.get('L_G_ratio', 15.0)
    
    def calculate_removal(self, gas_flow_nm3_h: float, SO2_in_ppm: float, SO3_in_ppm: float = 0.0) -> SOxRemovalResult:
        pH_eff = max(4.0, self.slurry_pH)
        eta = 1.0 - np.exp(-0.15 * self.L_G_ratio * (pH_eff - 4.0) / 5.0)
        SO2_out = float(SO2_in_ppm * (1.0 - eta))
        SO3_out = float(SO3_in_ppm * 0.01)
        
        SO2_removed_kg = (SO2_in_ppm - SO2_out) / 1e6 * gas_flow_nm3_h * (64.066 / 22.414)
        limestone_kg = SO2_removed_kg * (100.087 / 64.066) * 1.1
        gypsum_kg = SO2_removed_kg * (136.14 / 64.066)
        
        total_in = SO2_in_ppm + SO3_in_ppm
        total_out = SO2_out + SO3_out
        eff = (1.0 - total_out / max(total_in, 1e-6)) * 100.0
        
        return SOxRemovalResult(
            SO2_in=SO2_in_ppm,
            SO2_out=SO2_out,
            SO3_in=SO3_in_ppm,
            SO3_out=SO3_out,
            removal_efficiency=float(eff),
            limestone_consumed=float(limestone_kg),
            gypsum_produced=float(gypsum_kg),
            wastewater_volume=float(gas_flow_nm3_h * self.L_G_ratio / 10000.0),
            ph_drift=-0.05,
        )


class DualAlkaliSOxScrubber:
    """Dual alkali scrubber model."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def calculate_removal(self, gas_flow_nm3_h: float, SO2_in_ppm: float) -> Dict:
        eff = 98.5
        SO2_out = SO2_in_ppm * (1.0 - eff / 100.0)
        return {
            'SO2_in': SO2_in_ppm,
            'SO2_out': SO2_out,
            'efficiency': eff,
            'NaOH_consumed_kg_h': (SO2_in_ppm - SO2_out) * 1.25,
            'gypsum_produced_kg_h': (SO2_in_ppm - SO2_out) * 2.12,
        }
