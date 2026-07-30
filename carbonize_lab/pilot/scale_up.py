"""
Scale-up Analysis & Dimensionless Correlations
"""
import numpy as np
from typing import Dict, List


class ScaleUpAnalysis:
    @staticmethod
    def dimensional_analysis(pilot: Dict, plant: Dict) -> Dict:
        L_ratio = plant['length'] / pilot['length']
        D_ratio = plant['diameter'] / pilot['diameter']
        u_ratio = pilot['diameter'] / plant['diameter']
        tau_ratio = L_ratio / max(u_ratio, 1e-5)
        return {
            'geometric_ratio': {'length': float(L_ratio), 'diameter': float(D_ratio)},
            'velocity_ratio': float(u_ratio),
            'residence_time_ratio': float(tau_ratio),
            'recommendation': 'Reynolds similitude requires velocity scaling.',
        }

    @staticmethod
    def performance_correlation(pilot_data: List[Dict]) -> Dict:
        X = np.array([[p['diameter']] for p in pilot_data])
        y = np.array([p['capacity'] for p in pilot_data])
        log_X = np.log(X.flatten())
        log_y = np.log(y)
        n, log_k = np.polyfit(log_X, log_y, 1)
        return {
            'k': float(np.exp(log_k)),
            'n': float(n),
            'equation': f'Capacity = {np.exp(log_k):.2f} * D^{n:.2f}',
            'R_squared': float(np.corrcoef(log_X, log_y)[0, 1] ** 2),
        }
