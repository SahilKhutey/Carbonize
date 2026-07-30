"""
Catalyst and Adsorbent Design for Pollutant Control
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CatalystCandidate:
    name: str
    active_metal: str
    support: str
    promoter: Optional[str] = None
    conversion_target: float = 0.0
    TOF: float = 0.0
    selectivity: Dict[str, float] = None
    activation_energy: float = 0.0
    surface_area: float = 0.0
    pore_volume: float = 0.0
    mean_pore_size: float = 0.0
    metal_dispersion: float = 0.0
    thermal_stability: float = 0.0
    sulfur_tolerance: float = 0.0
    poison_resistance: float = 0.0
    expected_lifetime_years: float = 0.0
    synthesis_complexity: int = 0
    cost_USD_kg: float = 0.0
    scalability: float = 0.0
    score: float = 0.0


class CatalystDesigner:
    def __init__(self):
        self.metals_db = {
            'Pt': {'d-band': -1.8, 'cost_USD_g': 30.0, 'TOF_NH3_SCR': 2.0},
            'Pd': {'d-band': -1.6, 'cost_USD_g': 25.0, 'TOF_NH3_SCR': 1.5},
            'Rh': {'d-band': -1.7, 'cost_USD_g': 80.0, 'TOF_NH3_SCR': 5.0},
            'V': {'d-band': -1.0, 'cost_USD_g': 0.5, 'TOF_NH3_SCR': 1.0},
            'Cu': {'d-band': -1.5, 'cost_USD_g': 0.01, 'TOF_NH3_SCR': 0.8},
            'Fe': {'d-band': -1.0, 'cost_USD_g': 0.001, 'TOF_NH3_SCR': 0.3},
            'Mn': {'d-band': -0.8, 'cost_USD_g': 0.01, 'TOF_NH3_SCR': 0.4},
        }
        self.supports_db = {
            'TiO2': {'surface_area': 50.0, 'thermal_stability': 0.95, 'sulfur_tolerance': 0.1},
            'Al2O3': {'surface_area': 200.0, 'thermal_stability': 0.85, 'sulfur_tolerance': 0.4},
            'SiO2': {'surface_area': 300.0, 'thermal_stability': 0.6, 'sulfur_tolerance': 0.3},
            'CeO2': {'surface_area': 80.0, 'thermal_stability': 0.9, 'sulfur_tolerance': 0.5},
            'ZrO2': {'surface_area': 60.0, 'thermal_stability': 0.95, 'sulfur_tolerance': 0.7},
        }

    def design_scr_catalyst(self, target_conversion: float = 0.95, operating_T: float = 623.0) -> List[CatalystCandidate]:
        candidates = [
            self._build_catalyst('V2O5/WO3/TiO2', 'V', 'TiO2', 'W', operating_T, target_conversion),
            self._build_catalyst('Cu-SSZ-13', 'Cu', 'Al2O3', None, operating_T, target_conversion),
            self._build_catalyst('Fe-SSZ-13', 'Fe', 'Al2O3', None, operating_T, target_conversion),
            self._build_catalyst('Mn-Ce/TiO2', 'Mn', 'TiO2', 'Ce', operating_T, target_conversion),
        ]
        for c in candidates:
            c.score = self._catalyst_score(c)
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def _build_catalyst(self, name: str, active_metal: str, support: str, promoter: Optional[str], operating_T: float, target_conversion: float) -> CatalystCandidate:
        metal = self.metals_db.get(active_metal, {})
        sup = self.supports_db.get(support, {})
        base_TOF = metal.get('TOF_NH3_SCR', 0.5)
        Ea = 60.0
        R = 8.314e-3
        T_ref = 573.0
        T_factor = np.exp(-Ea / R * (1.0 / operating_T - 1.0 / T_ref))
        TOF = base_TOF * T_factor
        dispersion = 5.0 * (1.5 if promoter else 1.0)
        surface_area = sup.get('surface_area', 100.0) * (1 + dispersion / 10.0)
        metal_cost = metal.get('cost_USD_g', 1.0) * 0.05
        support_cost = 20.0
        promoter_cost = self.metals_db.get(promoter, {}).get('cost_USD_g', 0.0) * 0.03 if promoter else 0.0
        total_cost = metal_cost + support_cost + promoter_cost
        complexity = 5 if 'SSZ-13' in name else (3 if promoter else 2)

        return CatalystCandidate(
            name=name,
            active_metal=active_metal,
            support=support,
            promoter=promoter,
            conversion_target=target_conversion,
            TOF=float(TOF),
            selectivity={'N2': 0.95, 'N2O': 0.04, 'NO2': 0.01},
            activation_energy=60.0,
            surface_area=float(surface_area),
            pore_volume=0.5,
            mean_pore_size=10.0,
            metal_dispersion=float(dispersion),
            thermal_stability=sup.get('thermal_stability', 0.8),
            sulfur_tolerance=sup.get('sulfur_tolerance', 0.3),
            poison_resistance=0.7,
            expected_lifetime_years=3.0,
            synthesis_complexity=complexity,
            cost_USD_kg=float(total_cost),
            scalability=0.8,
        )

    def _catalyst_score(self, c: CatalystCandidate) -> float:
        s_TOF = min(1.0, c.TOF / 5.0)
        s_conv = 0.95
        s_sel = c.selectivity.get('N2', 0.9)
        s_stab = (c.thermal_stability + c.sulfur_tolerance + c.poison_resistance) / 3.0
        s_life = min(1.0, c.expected_lifetime_years / 5.0)
        s_cost = max(0.0, 1.0 - c.cost_USD_kg / 100.0)
        s_complex = 1.0 - (c.synthesis_complexity - 1) / 4.0
        s_scal = c.scalability
        score = (0.20 * s_TOF + 0.15 * s_conv + 0.15 * s_sel + 0.15 * s_stab + 0.10 * s_life + 0.10 * s_cost + 0.05 * s_complex + 0.10 * s_scal) * 100.0
        return float(max(0.0, min(100.0, score)))


class AdsorbentDesigner:
    def __init__(self):
        self.carbon_precursors = {
            'Coconut shell': {'surface_area': 1100, 'micropore_vol': 0.45, 'cost': 4.0},
            'Bituminous coal': {'surface_area': 900, 'micropore_vol': 0.35, 'cost': 3.0},
            'Wood-based': {'surface_area': 700, 'micropore_vol': 0.30, 'cost': 2.5},
            'Impregnated AC': {'surface_area': 950, 'micropore_vol': 0.40, 'cost': 8.0},
            'S-doped carbon': {'surface_area': 1100, 'micropore_vol': 0.48, 'cost': 6.0},
        }

    def design_mercury_sorbent(self, target_Hg_removal: float = 0.95) -> List[Dict]:
        candidates = []
        for name, props in self.carbon_precursors.items():
            halogenated = 'S' in name or 'Impregnated' in name
            base_removal = 0.93 if halogenated else 0.85
            sa_factor = props['surface_area'] / 1000.0
            removal = base_removal * (0.8 + 0.2 * sa_factor)
            candidates.append({
                'name': name,
                'removal_efficiency': float(removal),
                'surface_area': props['surface_area'],
                'cost_USD_kg': props['cost'],
                'score': float(removal * 100.0 - props['cost'] * 5.0),
                'halogenated': halogenated,
            })
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates
