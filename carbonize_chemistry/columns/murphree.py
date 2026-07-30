"""
Murphree efficiency calculations
"""

class MurphreeEfficiency:
    """Murphree stage efficiency module."""
    
    def __init__(self, E_MV: float = 0.75):
        self.E_MV = E_MV
    
    def calculate_vapor_out(self, y_in: float, y_eq: float) -> float:
        """Calculate vapor phase outlet composition using Murphree efficiency."""
        return y_in + self.E_MV * (y_eq - y_in)
