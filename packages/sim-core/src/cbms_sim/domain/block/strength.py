"""
domain/block/strength.py
Predicts composite solid properties (compressive strength, leaching classes).
"""

import numpy as np
from typing import Any
from cbms_sim.domain.models.results import MassBalanceResult
from cbms_sim.domain.models.conditions import OperatingConditions

class BlockStrengthPredictor:
    """Predicts mechanical parameters of formed calcite/gypsum/fly ash blocks."""
    
    def predict(self, mb: MassBalanceResult, conditions: OperatingConditions) -> dict[str, Any]:
        """Empirical formulation mapping dry inorganic density to strength."""
        caco3 = mb.caco3_output_kg_hr
        gypsum = mb.gypsum_output_kg_hr
        ash = mb.fly_ash_captured_kg_hr
        chitosan = mb.chitosan_solid_kg_hr
        
        # Calculate dry mass ratios
        dry_total = caco3 + gypsum + ash + chitosan
        if dry_total <= 0:
            return {
                "compressive_strength_mpa": 0.0,
                "is_grade": "SUBSTANDARD",
                "absorption_pct": 100.0,
                "leach_risk_class": "HIGH"
            }
            
        ash_frac = ash / dry_total
        chitosan_frac = chitosan / dry_total
        press = float(conditions.press_force_bar)
        cure_h = float(conditions.curing_time_h)
        
        # Grounded empirical strength formula with curing saturation & non-degenerate pressure scaling
        curing_factor = 1.0 - np.exp(-cure_h / 24.0)
        pressure_factor = np.log10(press / 10.0 + 1.0)
        
        strength = 20.0 * (1.0 + 1.2 * ash_frac) * pressure_factor * (chitosan_frac / 0.03) * curing_factor
        strength = max(1.0, min(strength, 60.0))
        
        # Assign Grade
        if strength >= 25.0:
            grade = "M25"
        elif strength >= 20.0:
            grade = "M20"
        elif strength >= 10.0:
            grade = "M10"
        else:
            grade = "SUBSTANDARD"
            
        # Absorption
        absorption = max(5.0, 20.0 - 0.02 * press - 15.0 * chitosan_frac)
        
        # Leaching class
        leach_class = "LOW" if chitosan_frac >= 0.025 else "MEDIUM"
        
        return {
            "compressive_strength_mpa": strength,
            "is_grade": grade,
            "absorption_pct": absorption,
            "leach_risk_class": leach_class
        }
