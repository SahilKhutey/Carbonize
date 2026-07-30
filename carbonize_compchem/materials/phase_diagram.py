"""
Phase Diagram Calculations (CALPHAD-style)
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class Phase:
    name: str
    structure: str
    components: List[str]
    G_ser: Dict[str, float] = field(default_factory=dict)
    L_params: Dict = field(default_factory=dict)

    def gibbs_energy(self, T: float, x: Dict[str, float]) -> float:
        G_ref = sum(x.get(e, 0.0) * self.G_ser.get(e, 0.0) for e in x)
        R = 8.314
        G_ideal = sum(R * T * xi * np.log(max(xi, 1e-10)) for xi in x.values() if xi > 0)
        return float(G_ref + G_ideal)


class PhaseDiagram:
    def __init__(self, system_name: str):
        self.name = system_name
        self.phases: Dict[str, Phase] = {}
        self.components: List[str] = []

    def add_phase(self, phase: Phase):
        self.phases[phase.name] = phase

    def binary_phase_diagram(self, T_range: Tuple[float, float], n_T: int = 50) -> Dict:
        temps = np.linspace(T_range[0], T_range[1], n_T)
        mole_fracs = np.linspace(0.0, 1.0, 50)
        dominant = np.zeros((n_T, 50), dtype=int)
        return {
            'temperatures': temps.tolist(),
            'mole_fractions': mole_fracs.tolist(),
            'dominant_phase': dominant.tolist(),
            'phase_names': list(self.phases.keys()),
        }
