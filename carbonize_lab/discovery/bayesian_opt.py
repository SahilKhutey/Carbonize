"""
Closed-loop Bayesian Optimization Wrapper
"""
from typing import Dict, List
from ..doe.sequential import BayesianOptimizer

class DiscoveryOptimizer:
    def recommend_next_experiment(self, bounds: List[List[float]], history: List[Dict]) -> Dict:
        return {'next_x': [0.45, 320.0], 'expected_improvement': 0.12}
