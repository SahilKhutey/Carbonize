"""
Validation on Ishigami function.
"""

import numpy as np
import pytest

from .toy_problems import (
    ishigami, ishigami_sobol_analytical
)


class TestIshigamiFunction:
    """Comprehensive Ishigami function validation."""
    
    def test_ishigami_first_order_indices(self, reference_salib):
        """
        VALIDATION: Our S1 indices for Ishigami match known values.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        # Large N for accuracy
        N = 8192
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        # Our implementation
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
        )
        
        # Known analytical values
        expected = ishigami_sobol_analytical()
        
        # Verify
        for i, name in enumerate(['x1', 'x2', 'x3']):
            our_s1 = our_result["first_order"][name]
            expected_s1 = expected["first_order"][name]
            
            if expected_s1 == 0.0:
                assert abs(our_s1) < 0.05
            else:
                abs_err = abs(our_s1 - expected_s1)
                assert abs_err < 0.03, \
                    f"S1[{name}]: ours={our_s1:.4f}, expected={expected_s1:.4f}"
    
    def test_ishigami_total_order_indices(self, reference_salib):
        """
        VALIDATION: Our ST indices for Ishigami match known values.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        N = 8192
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
        )
        
        expected = ishigami_sobol_analytical()
        
        for i, name in enumerate(['x1', 'x2', 'x3']):
            our_st = our_result["total_order"][name]
            expected_st = expected["total_order"][name]
            
            abs_err = abs(our_st - expected_st)
            assert abs_err < 0.03, \
                f"ST[{name}]: ours={our_st:.4f}, expected={expected_st:.4f}"
    
    def test_ishigami_x3_has_no_first_order(self, reference_salib):
        """
        VALIDATION: In Ishigami, X3 has zero first-order effect
        (only via interaction with X1).
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        N = 8192
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
        )
        
        s1_x3 = our_result["first_order"]["x3"]
        assert abs(s1_x3) < 0.03, \
            f"X3 first-order should be ≈ 0, got {s1_x3:.4f}"
        
        st_x3 = our_result["total_order"]["x3"]
        assert st_x3 > 0.20, \
            f"X3 total-order should be > 0.20, got {st_x3:.4f}"
        
        assert st_x3 > s1_x3 + 0.15
