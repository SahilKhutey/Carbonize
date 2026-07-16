"""
Validation on the G* function.
"""

import numpy as np
import pytest

from .toy_problems import g_func


class TestGFunction:
    """Validate Sobol indices on the standard 8D G* function."""
    
    def test_g_func_sobol_indices(self, reference_salib):
        """
        VALIDATION: Verify first-order and total-order Sobol indices
        for G* function match SALib.
        """
        from SALib.sample import sobol
        from SALib.analyze import sobol as salib_sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 8,
            'names': [f"x{i+1}" for i in range(8)],
            'bounds': [[0, 1]] * 8
        }
        
        N = 2048
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([g_func(x) for x in param_values])
        
        # SALib reference
        salib_result = salib_sobol.analyze(
            problem, Y, calc_second_order=False, print_to_console=False
        )
        
        # Our implementation
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=8, calc_second_order=False, names=problem['names']
        )
        
        # Compare ours directly to SALib
        for i, name in enumerate(problem['names']):
            our_s1 = our_result["first_order"][name]
            salib_s1 = salib_result["S1"][i]
            
            assert abs(our_s1 - salib_s1) < 0.05, f"S1[{name}]: ours={our_s1:.4f}, SALib={salib_s1:.4f}"
                
            our_st = our_result["total_order"][name]
            salib_st = salib_result["ST"][i]
            
            assert abs(our_st - salib_st) < 0.05, f"ST[{name}]: ours={our_st:.4f}, SALib={salib_st:.4f}"
