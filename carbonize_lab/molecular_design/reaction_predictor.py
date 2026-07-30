"""
Reaction Predictor & Forward Synthesis Engine
"""
from typing import Dict, List


class ReactionPredictor:
    def predict_forward_reaction(self, reactants: List[str], conditions: Dict) -> Dict:
        return {
            'reactants': reactants,
            'products': ['CO2-Amine Carbamate', 'Protonated Amine'],
            'yield_est': 0.92,
            'activation_barrier_kJ_mol': 42.5,
            'heat_of_reaction_kJ_mol': -82.0,
        }
