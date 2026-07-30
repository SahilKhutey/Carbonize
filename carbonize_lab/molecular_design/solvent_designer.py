"""
Solvent design for CO2 capture and pollutant control
Uses COSMO-RS sigma profiles + group contribution methods
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SolventCandidate:
    """Candidate solvent for CO2 capture."""
    name: str
    structure: str
    functional_groups: List[str]
    molecular_weight: float = 0.0
    boiling_point: float = 0.0
    melting_point: float = 0.0
    density: float = 0.0
    viscosity_25C: float = 0.0
    pKa: float = 0.0
    pKb: float = 0.0
    CO2_loading_max: float = 0.0
    cyclic_capacity: float = 0.0
    absorption_rate: float = 0.0
    regeneration_energy: float = 0.0
    heat_of_reaction: float = 0.0
    toxicity_LD50: float = 0.0
    biodegradability: float = 0.0
    vapor_pressure: float = 0.0
    flash_point: float = 0.0
    cost_USD_kg: float = 0.0
    global_production_kt: float = 0.0
    overall_score: float = 0.0
    degradation_rate: float = 0.0
    oxidative_stability: float = 0.0
    thermal_stability: float = 0.0


class COSMORS_SolventDesigner:
    """COSMO-RS-based solvent design using sigma profiles and interaction energetics."""

    def __init__(self):
        self.sigma_db = {
            'H2O': {'sigma_profile': np.array([-0.025, -0.020, -0.015, -0.010, 0.000, 0.005, 0.010, 0.015, 0.020, 0.025]), 'molecular_area': 53.7, 'molecular_volume': 25.3},
            'MEA': {'sigma_profile': np.array([-0.020, -0.015, -0.010, -0.005, 0.000, 0.005, 0.010, 0.015, 0.020, 0.025]), 'molecular_area': 73.5, 'molecular_volume': 76.8},
            'MDEA': {'sigma_profile': np.array([-0.020, -0.015, -0.010, -0.005, 0.000, 0.005, 0.010, 0.015, 0.020]), 'molecular_area': 105.2, 'molecular_volume': 143.5},
            'Piperazine': {'sigma_profile': np.array([-0.025, -0.020, -0.015, -0.010, 0.000, 0.005, 0.010, 0.015, 0.020]), 'molecular_area': 87.4, 'molecular_volume': 87.1},
            'AMP': {'sigma_profile': np.array([-0.020, -0.015, -0.010, -0.005, 0.000, 0.005, 0.010, 0.015, 0.020]), 'molecular_area': 89.3, 'molecular_volume': 92.4},
        }

    def predict_CO2_solubility(self, solvent: str, T: float = 313.15, P_CO2: float = 15000.0) -> float:
        if solvent not in self.sigma_db:
            raise ValueError(f"Sigma profile not available for {solvent}")
        profile = self.sigma_db[solvent]
        E_misfit = 0.0
        sigma_CO2 = 0.014
        for sigma_s in profile['sigma_profile']:
            E_misfit += (sigma_s - sigma_CO2) ** 2 * 0.7

        E_HB_donor = 0.0
        for sigma_s in profile['sigma_profile']:
            if sigma_s < -0.0085:
                E_HB_donor += (sigma_s + 0.0085) ** 2 * 5160.0
        E_HB_donor = -E_HB_donor

        E_vdW = 0.0
        for sigma_s in profile['sigma_profile']:
            if sigma_s < 0.0085:
                E_vdW += 0.06 * (sigma_s - sigma_CO2) ** 2 * 9.0

        E_total = E_misfit + E_HB_donor + E_vdW
        R = 8.314
        gamma = np.exp(E_total / (R * T))
        P_vap_water = 101325.0
        ratio_M = self._molecular_weight(solvent) / 18.015
        H_CO2 = gamma * P_vap_water * ratio_M ** 0.5
        loading = (P_CO2 / max(H_CO2, 1e-5)) / 0.3
        return float(max(0.0, min(loading, 2.0)))

    def _molecular_weight(self, solvent: str) -> float:
        return {'H2O': 18.015, 'MEA': 61.08, 'MDEA': 119.16, 'Piperazine': 86.14, 'AMP': 89.14}.get(solvent, 100.0)

    def predict_heat_of_absorption(self, solvent: str) -> float:
        base_heat = {'MEA': 85.0, 'MDEA': 60.0, 'Piperazine': 70.0, 'AMP': 75.0, 'H2O': 20.0}.get(solvent, 80.0)
        corrections = {'MEA': -5.0, 'MDEA': 0.0, 'Piperazine': -10.0}
        return float(base_heat + corrections.get(solvent, 0.0))

    def screen_amine_solvent(self, amino_group: str, additional_groups: List[str] = None) -> SolventCandidate:
        base_smiles = {'primary': 'NCO', 'secondary': 'N(C)C', 'tertiary': 'N(C)(C)C', 'sterically_hindered': 'NC(C)(C)C'}
        groups = ['-NH2', '-OH', '-CH2-']
        if additional_groups:
            groups.extend(additional_groups)

        prop = self._group_contribution(groups)
        pKa = self._estimate_pka(groups)
        max_loading = self._estimate_max_loading(amino_group, additional_groups)
        dH = self._estimate_dH(groups)
        cyclic = max_loading * 0.8
        rate = self._estimate_rate(pKa, amino_group)
        ox_stab = self._estimate_oxidative_stability(amino_group)
        therm_stab = 0.95 if amino_group in ['primary', 'secondary'] else 0.85
        toxicity = self._estimate_toxicity(groups)
        cost = self._estimate_cost(groups)
        score = self._composite_score(cyclic, rate, dH, ox_stab, therm_stab, toxicity, cost)

        return SolventCandidate(
            name=f"Hypothetical amine ({amino_group})",
            structure=base_smiles.get(amino_group, 'NCO'),
            functional_groups=groups,
            molecular_weight=prop['MW'],
            boiling_point=prop['Tb'],
            melting_point=prop['Tm'],
            density=prop['density'],
            viscosity_25C=prop['viscosity'],
            pKa=pKa,
            CO2_loading_max=max_loading,
            cyclic_capacity=cyclic,
            absorption_rate=rate,
            regeneration_energy=dH * 0.5,
            heat_of_reaction=dH,
            toxicity_LD50=toxicity,
            biodegradability=0.7,
            vapor_pressure=10.0,
            flash_point=380.0,
            cost_USD_kg=cost,
            global_production_kt=100.0,
            overall_score=score,
            oxidative_stability=ox_stab,
            thermal_stability=therm_stab,
        )

    def _group_contribution(self, groups: List[str]) -> Dict:
        params = {
            '-NH2': {'Tb': 50.0, 'Tm': 30.0, 'MW': 16.0, 'density': 0.95},
            '-NH-': {'Tb': 45.0, 'Tm': 20.0, 'MW': 15.0, 'density': 0.92},
            '-N<': {'Tb': 30.0, 'Tm': 0.0, 'MW': 14.0, 'density': 0.90},
            '-OH': {'Tb': 95.0, 'Tm': 50.0, 'MW': 17.0, 'density': 1.10},
            '-CH2-': {'Tb': 25.0, 'Tm': 5.0, 'MW': 14.0, 'density': 0.85},
            '-CH3': {'Tb': 20.0, 'Tm': 0.0, 'MW': 15.0, 'density': 0.80},
        }
        MW = sum(params.get(g, {}).get('MW', 14.0) for g in groups)
        Tb = 273.0 + sum(params.get(g, {}).get('Tb', 20.0) for g in groups)
        Tm = sum(params.get(g, {}).get('Tm', 5.0) for g in groups)
        density = 950.0
        return {'MW': float(MW), 'Tb': float(Tb), 'Tm': float(Tm), 'density': float(density), 'viscosity': 1e-3 * (1 + MW / 100.0)}

    def _estimate_pka(self, groups: List[str]) -> float:
        if '-NH2' in groups: return 10.5
        if '-NH-' in groups: return 11.0
        if '-N<' in groups: return 9.5
        return 8.0

    def _estimate_max_loading(self, amino_type: str, additional_groups: Optional[List[str]]) -> float:
        return {'primary': 0.5, 'secondary': 0.5, 'tertiary': 1.0, 'sterically_hindered': 0.5}.get(amino_type, 0.5)

    def _estimate_dH(self, groups: List[str]) -> float:
        if '-NH2' in groups: return 85.0
        if '-NH-' in groups: return 70.0
        if '-N<' in groups: return 60.0
        return 80.0

    def _estimate_rate(self, pKa: float, amino_type: str) -> float:
        if amino_type == 'sterically_hindered': return 5.0
        return float(100.0 * 10 ** (pKa - 10.0))

    def _estimate_oxidative_stability(self, amino_type: str) -> float:
        return {'primary': 0.5, 'secondary': 0.7, 'tertiary': 0.9, 'sterically_hindered': 0.85}.get(amino_type, 0.7)

    def _estimate_toxicity(self, groups: List[str]) -> float:
        if '-NH2' in groups: return 1500.0
        if '-NH-' in groups: return 2000.0
        return 3000.0

    def _estimate_cost(self, groups: List[str]) -> float:
        return 2.0 + len(groups) * 0.5

    def _composite_score(self, cyclic, rate, dH, ox_stab, therm_stab, tox, cost) -> float:
        s_cyclic = min(1.0, cyclic / 0.5)
        s_rate = min(1.0, rate / 50.0) if rate else 0.0
        s_dH = max(0.0, 1.0 - (dH - 50.0) / 100.0)
        s_stab = (ox_stab + therm_stab) / 2.0
        s_tox = min(1.0, tox / 3000.0)
        s_cost = max(0.0, 1.0 - cost / 5.0)
        score = (0.25 * s_cyclic + 0.15 * s_rate + 0.20 * s_dH + 0.15 * s_stab + 0.10 * s_tox + 0.15 * s_cost) * 100.0
        return float(max(0.0, min(100.0, score)))


class AmineMixtureDesigner:
    def __init__(self):
        self.cosmo = COSMORS_SolventDesigner()

    def evaluate_mixture(self, components: Dict[str, float]) -> Dict:
        total_MW = sum(self.cosmo._molecular_weight(name) * frac for name, frac in components.items())
        cyclic = sum(0.5 * frac for name, frac in components.items())
        dH = sum(self.cosmo.predict_heat_of_absorption(name) * frac for name, frac in components.items())
        rates = [self.cosmo.screen_amine_solvent(name).absorption_rate for name in components.keys()]
        max_rate = max(rates) if rates else 50.0
        stabilities = {'MEA': 0.5, 'MDEA': 0.9, 'Piperazine': 0.85, 'AMP': 0.8}
        worst_stability = min(stabilities.get(name, 0.7) for name in components.keys())
        return {
            'cyclic_capacity': float(cyclic),
            'MW': float(total_MW),
            'heat_of_absorption': float(dH),
            'rate': float(max_rate),
            'stability': float(worst_stability),
            'composition': components,
        }
