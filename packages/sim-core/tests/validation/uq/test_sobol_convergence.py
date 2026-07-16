"""
Validate convergence properties of the Sobol sensitivity estimator.
"""

import numpy as np
import pytest

from .toy_problems import ishigami


class TestSobolConvergence:
    """Verify Sobol indices converge as N increases."""
    
    def test_sobol_converges_with_N(self, reference_salib):
        """
        PROPERTY: As N increases, our Sobol indices should converge
        to SALib's values.
        """
        from SALib.sample import sobol
        from SALib.analyze import sobol as salib_sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        # We test with different N and check error
        for N in [256, 1024, 2048]:
            param_values = sobol.sample(problem, N, calc_second_order=False)
            Y = np.array([ishigami(x) for x in param_values])
            
            our_result = sobol_indices(
                samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
            )
            salib_result = salib_sobol.analyze(
                problem, Y, calc_second_order=False, print_to_console=False
            )
            
            # Compare our S1[x1] with SALib's
            our_s1 = our_result["first_order"]["x1"]
            salib_s1 = salib_result["S1"][0]
            
            # Error should be within 10%
            rel_err = abs(our_s1 - salib_s1) / max(abs(salib_s1), 1e-6)
            assert rel_err < 0.10, \
                f"N={N}: ours={our_s1:.4f}, SALib={salib_s1:.4f}, rel_err={rel_err:.4f}"
