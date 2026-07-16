"""
LHS sampling algorithms for CBMS simulation.
"""

import numpy as np
from scipy.stats import qmc


def lh_sample(n: int, n_vars: int, seed: int = 42) -> np.ndarray:
    """
    Generate Latin Hypercube Samples in [0, 1]^n_vars.
    
    Args:
        n: Number of samples to generate.
        n_vars: Number of parameters/variables.
        seed: Random seed for reproducibility.
        
    Returns:
        np.ndarray of shape (n, n_vars) with values in [0, 1].
    """
    sampler = qmc.LatinHypercube(d=n_vars, seed=seed)
    return sampler.random(n=n)
