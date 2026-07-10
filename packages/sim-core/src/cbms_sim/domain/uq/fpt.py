"""
domain/uq/fpt.py
Implements First Passage Time (FPT) using Wiener process drift/diffusion models.
"""

from typing import Dict, Any
import numpy as np

class FirstPassageTime:
    """Calculates Wiener stochastic properties for reactor saturation times."""
    
    def analytical_fpt(self, threshold: float, drift: float, diffusion: float) -> dict[str, float]:
        """Analytical Inverse Gaussian first-passage time properties."""
        if drift <= 0:
            mean = float('inf')
            mode = 0.0
        else:
            mean = threshold / drift
            mode = (mean * (np.sqrt(1.0 + 9.0 * (diffusion ** 2) / (4.0 * (drift ** 2) * mean)) - 3.0 * diffusion / (2.0 * drift)))
            
        variance = (threshold * (diffusion ** 2)) / (drift ** 3) if drift > 0 else float('inf')
        
        return {
            "mean_fpt_hours": mean,
            "mode_fpt_hours": mode,
            "variance_fpt_hours": variance
        }
