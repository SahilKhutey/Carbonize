"""
Statistical Ensembles (NVE, NVT, NPT, muVT)
"""
class Ensemble:
    def __init__(self, ensemble_type: str = 'NVT'):
        self.type = ensemble_type
