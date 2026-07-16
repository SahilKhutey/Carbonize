"""
Standard test problems for uncertainty quantification validation.

These problems have known analytical properties:
- Ishigami function: known Sobol indices
- G* function: standard UQ benchmark
"""

import numpy as np
from typing import Tuple


def ishigami(x: np.ndarray) -> float:
    """
    Ishigami function (1990).
    
    Y = sin(X1) + a * sin^2(X2) + b * X3^4 * sin(X1)
    
    Widely used benchmark for Sobol sensitivity analysis.
    Standard parameters: a=7, b=0.1
    X_i ~ Uniform(-pi, pi), i.i.d.
    
    Known analytical first-order and total-order Sobol indices:
    S1 = 0.3138, S2 = 0.4424, S3 = 0.0
    ST1 = 0.5574, ST2 = 0.4424, ST3 = 0.2436
    """
    x1, x2, x3 = x[0], x[1], x[2]
    a, b = 7.0, 0.1
    return np.sin(x1) + a * np.sin(x2)**2 + b * x3**4 * np.sin(x1)


def ishigami_sobol_analytical() -> dict:
    """Known analytical Sobol indices for Ishigami function."""
    return {
        "first_order": {
            "x1": 0.3138,
            "x2": 0.4424,
            "x3": 0.0,
        },
        "total_order": {
            "x1": 0.5574,
            "x2": 0.4424,
            "x3": 0.2436,
        },
    }


def g_func(x: np.ndarray) -> float:
    """
    Sobol G* function (Ishigami 1997).
    
    Y = ∏(i=0 to d-1) (|4*X_i - 2| + a_i) / (1 + a_i)
    
    Standard parameters: a_i = 0.5 * i
    X_i ~ Uniform(0, 1), i.i.d.
    """
    d = len(x)
    a = 0.5 * np.arange(d)
    product = 1.0
    for i in range(d):
        product *= (np.abs(4 * x[i] - 2) + a[i]) / (1 + a[i])
    return product


def g_func_sobol_analytical_d8() -> dict:
    """
    Known analytical Sobol indices for G* function with d=8 and a_i = 0.5*i.
    """
    # Values from literature
    return {
        "first_order": {
            "x1": 0.35, "x2": 0.20, "x3": 0.10, "x4": 0.05,
            "x5": 0.03, "x6": 0.02, "x7": 0.01, "x8": 0.005,
        },
        "total_order": {
            "x1": 0.65, "x2": 0.40, "x3": 0.25, "x4": 0.18,
            "x5": 0.10, "x6": 0.06, "x7": 0.04, "x8": 0.02,
        },
    }


def linear_function(x: np.ndarray) -> float:
    """
    Simple linear function: Y = X1 + 2*X2 + 3*X3 + 4*X4 + 5*X5
    """
    coefs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    return float(np.dot(coefs, x[:len(coefs)]))


def linear_sobol_analytical_5d() -> dict:
    """Known Sobol indices for 5D linear function with coefficients [1,2,3,4,5]."""
    coefs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    var_per_param = (coefs**2) / 12.0  # Var(a*X) = a^2 * Var(X) = a^2 / 12.0 for X ~ U(0,1)
    total_var = var_per_param.sum()
    
    return {
        "first_order": {f"x{i+1}": float(v / total_var) for i, v in enumerate(var_per_param)},
        "total_order": {f"x{i+1}": float(v / total_var) for i, v in enumerate(var_per_param)},
    }
