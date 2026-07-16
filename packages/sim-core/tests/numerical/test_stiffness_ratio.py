"""
Analyze the stiffness of the ODE system to verify BDF is appropriate.
"""

from __future__ import annotations

import numpy as np

from tests.numerical.conftest import make_reference_rhs, params_standard


def compute_jacobian_eigenvalues(rhs, y, t=0):
    n = len(y)
    J = np.zeros((n, n))
    eps = 1e-7
    
    f0 = rhs(t, y)
    for i in range(n):
        y_pert = y.copy()
        y_pert[i] += eps
        f_pert = rhs(t, y_pert)
        J[:, i] = (f_pert - f0) / eps
        
    return np.linalg.eigvals(J)


class TestStiffnessRatio:
    """The ratio of max to min |eigenvalue| determines stiffness."""
    
    def test_stiffness_justifies_bdf(self, params_standard):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        rhs = make_reference_rhs(params_standard)
        eigvals = compute_jacobian_eigenvalues(rhs, y0)
        
        real_eigvals = np.abs(eigvals.real)
        stiffness_ratio = real_eigvals.max() / max(real_eigvals.min(), 1e-15)
        
        # System IS stiff
        assert stiffness_ratio > 10.0, f"System not stiff enough: ratio = {stiffness_ratio:.1f}"
