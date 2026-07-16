"""
Validate our Sobol implementation against SALib.
"""

import numpy as np
import pytest

from .toy_problems import (
    ishigami,
    ishigami_sobol_analytical,
    linear_function,
    linear_sobol_analytical_5d,
)
from .comparison_helpers import (
    compare_sobol_indices,
    compute_agreement_metrics,
)


class TestSobolVsSALib:
    """Compare our Sobol indices to SALib's on the same problem."""
    
    def test_ishigami_matches_salib_within_tolerance(self, reference_salib):
        """
        PROPERTY: Our Sobol indices for the Ishigami function should
        match SALib's within tight tolerance (rtol=0.10).
        """
        from SALib.sample import sobol
        from SALib.analyze import sobol as salib_sobol
        
        # Define problem (3 variables, uniform [-π, π])
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        # Generate samples using SALib's Sobol scheme
        n = 1024  # Total = 1024*(3+2) = 5120
        param_values = sobol.sample(problem, n, calc_second_order=False)
        
        # Run model
        Y = np.array([ishigami(x) for x in param_values])
        
        # SALib analysis
        salib_result = salib_sobol.analyze(
            problem, Y, calc_second_order=False, print_to_console=False
        )
        
        # Our Sobol implementation
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        our_result = sobol_indices(
            samples=param_values,
            Y=Y,
            n_vars=3,
            calc_second_order=False,
            names=['x1', 'x2', 'x3']
        )
        
        # Compare indices
        for i, name in enumerate(['x1', 'x2', 'x3']):
            our_s1 = our_result["first_order"][name]
            salib_s1 = salib_result["S1"][i]
            
            rel_err = abs(our_s1 - salib_s1) / max(abs(salib_s1), 1e-6)
            assert rel_err < 0.10, \
                f"S1[{name}]: ours={our_s1:.4f}, SALib={salib_s1:.4f}, rel_err={rel_err:.4f}"
            
            our_st = our_result["total_order"][name]
            salib_st = salib_result["ST"][i]
            
            rel_err = abs(our_st - salib_st) / max(abs(salib_st), 1e-6)
            assert rel_err < 0.10, \
                f"ST[{name}]: ours={our_st:.4f}, SALib={salib_st:.4f}, rel_err={rel_err:.4f}"
    
    def test_ishigami_matches_analytical_values(self, reference_salib):
        """
        PROPERTY: Our Sobol indices should match the known analytical
        values for the Ishigami function.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        N = 4096
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        # Our implementation
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=['x1', 'x2', 'x3']
        )
        
        # Known analytical
        analytical = ishigami_sobol_analytical()
        
        for i, name in enumerate(['x1', 'x2', 'x3']):
            our_s1 = our_result["first_order"][name]
            expected_s1 = analytical["first_order"][name]
            
            # Since S1[x3] = 0 analytically, we compare absolute difference
            if expected_s1 == 0.0:
                assert abs(our_s1) < 0.05, f"S1[x3]: ours={our_s1:.4f}, expected=0"
            else:
                rel_err = abs(our_s1 - expected_s1) / expected_s1
                assert rel_err < 0.05, \
                    f"S1[{name}]: ours={our_s1:.4f}, expected={expected_s1:.4f}, rel_err={rel_err:.4f}"
            
            our_st = our_result["total_order"][name]
            expected_st = analytical["total_order"][name]
            
            rel_err = abs(our_st - expected_st) / expected_st
            assert rel_err < 0.05, \
                f"ST[{name}]: ours={our_st:.4f}, expected={expected_st:.4f}, rel_err={rel_err:.4f}"
    
    def test_linear_function_sobol_correct(self, reference_salib):
        """
        PROPERTY: For a linear function, first-order = total-order (no interactions).
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 5,
            'names': ['x1', 'x2', 'x3', 'x4', 'x5'],
            'bounds': [[0, 1]] * 5
        }
        
        N = 2048
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([linear_function(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=5, calc_second_order=False, names=problem['names']
        )
        
        # For linear function: S1 = ST (no interactions)
        for name in problem['names']:
            s1 = our_result["first_order"][name]
            st = our_result["total_order"][name]
            
            rel_diff = abs(s1 - st) / max(abs(s1), 1e-6)
            assert rel_diff < 0.05, \
                f"{name}: S1={s1:.4f}, ST={st:.4f} (should be equal for linear)"
        
        # Check analytical values
        analytical = linear_sobol_analytical_5d()
        for name in problem['names']:
            our_s1 = our_result["first_order"][name]
            expected = analytical["first_order"][name]
            
            rel_err = abs(our_s1 - expected) / expected
            assert rel_err < 0.05, \
                f"S1[{name}]: ours={our_s1:.4f}, expected={expected:.4f}"


class TestSobolProperties:
    """Properties that Sobol indices must satisfy."""
    
    def test_first_order_sum_at_most_1(self, reference_salib):
        """
        PROPERTY: Sum of first-order indices S1 should be <= 1.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 5,
            'names': ['x1', 'x2', 'x3', 'x4', 'x5'],
            'bounds': [[0, 1]] * 5
        }
        
        N = 2048
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([linear_function(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=5, calc_second_order=False, names=problem['names']
        )
        
        sum_s1 = sum(our_result["first_order"].values())
        assert sum_s1 <= 1.0 + 0.02, \
            f"Sum S1 = {sum_s1:.4f} should be <= 1"
    
    def test_total_order_at_least_first_order(self, reference_salib):
        """
        PROPERTY: For any parameter, ST >= S1.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        N = 2048
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
        )
        
        for name in problem['names']:
            s1 = our_result["first_order"][name]
            st = our_result["total_order"][name]
            
            # Allow tiny numerical tolerance
            assert st >= s1 - 0.01, \
                f"{name}: ST ({st:.4f}) should be >= S1 ({s1:.4f})"
    
    def test_indices_non_negative(self, reference_salib):
        """
        PROPERTY: Sobol indices are non-negative.
        """
        from SALib.sample import sobol
        from cbms_sim.domain.uq.sobol import sobol_indices
        
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi]] * 3
        }
        
        N = 2048
        param_values = sobol.sample(problem, N, calc_second_order=False)
        Y = np.array([ishigami(x) for x in param_values])
        
        our_result = sobol_indices(
            samples=param_values, Y=Y, n_vars=3, calc_second_order=False, names=problem['names']
        )
        
        for name in problem['names']:
            s1 = our_result["first_order"][name]
            st = our_result["total_order"][name]
            
            assert s1 >= -0.05, f"S1[{name}] = {s1:.4f} should be >= 0"
            assert st >= -0.05, f"ST[{name}] = {st:.4f} should be >= 0"
