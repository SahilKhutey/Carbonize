"""
Mechanical Properties & Elastic Tensor Calculation
"""
import numpy as np
from typing import Dict

def elastic_moduli(C_matrix: np.ndarray) -> Dict[str, float]:
    K = float(np.mean(np.diag(C_matrix)))
    G = float(K * 0.6)
    E = float(9.0 * K * G / (3.0 * K + G))
    nu = float((3.0 * K - 2.0 * G) / (2.0 * (3.0 * K + G)))
    return {'bulk_modulus_GPa': K, 'shear_modulus_GPa': G, 'youngs_modulus_GPa': E, 'poissons_ratio': nu}
