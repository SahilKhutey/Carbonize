"""
Mercury & Particulate removal
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class MercuryRemovalResult:
    Hg_in: float
    Hg_out: float
    oxidized_Hg_fraction: float
    removal_efficiency: float
    sorbent_consumed: float
    APC_residue: float


class ActivatedCarbonInjection:
    """Activated carbon injection for mercury capture."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def calculate_removal(self, gas_flow_nm3_h: float, Hg_in_ug_Nm3: float) -> MercuryRemovalResult:
        eff = 91.0
        Hg_out = Hg_in_ug_Nm3 * (1.0 - eff / 100.0)
        sorbent_kg = (Hg_in_ug_Nm3 - Hg_out) / 1e6 * gas_flow_nm3_h * 0.1
        return MercuryRemovalResult(
            Hg_in=Hg_in_ug_Nm3,
            Hg_out=Hg_out,
            oxidized_Hg_fraction=0.75,
            removal_efficiency=eff,
            sorbent_consumed=float(sorbent_kg),
            APC_residue=float(sorbent_kg * 1.4),
        )


class ESP_ParticulateRemoval:
    """Electrostatic precipitator model."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def calculate_removal(self, gas_flow: float, PM_in: float) -> Dict:
        eff = 99.8
        PM_out = PM_in * (1.0 - eff / 100.0)
        return {
            'PM_in_mg_Nm3': PM_in,
            'PM_out_mg_Nm3': PM_out,
            'efficiency': eff,
            'ash_produced_kg_h': (PM_in - PM_out) * gas_flow / 1e6,
        }
