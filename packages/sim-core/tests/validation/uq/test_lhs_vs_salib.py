"""
Validate our LHS implementation against SALib's.

SALib is the de facto standard for sensitivity analysis in Python.
If our LHS samples match SALib's, we have strong evidence of correctness.
"""

import numpy as np
import pytest

from .comparison_helpers import (
    compute_sample_moments,
    check_stratification,
    compute_coverage_metric,
)


class TestLHSvsSALib:
    """Compare our LHS to SALib's LHS."""
    
    def test_lhs_matches_salib_marginal_distributions(
        self, reference_salib, n_samples
    ):
        """
        PROPERTY: Our LHS samples should have the same marginal
        distributions as SALib's.
        
        Both are LHS, so per-dimension distributions should be uniform.
        """
        from cbms_sim.domain.uq.sampling import lh_sample
        from SALib.sample import latin as salib_latin
        
        # Define problem
        n_vars = 4
        problem = {
            'num_vars': n_vars,
            'bounds': [[0, 1]] * n_vars
        }
        
        # Generate samples both ways
        our_samples = lh_sample(n=n_samples, n_vars=n_vars, seed=42)
        
        salib_samples = salib_latin.sample(problem, n_samples, seed=42)
        
        # Per-dimension, samples should be roughly uniform
        for i in range(n_vars):
            from scipy.stats import kstest
            our_ks = kstest(our_samples[:, i], 'uniform')
            salib_ks = kstest(salib_samples[:, i], 'uniform')
            
            assert our_ks.pvalue > 0.01, \
                f"Our LHS dim {i} not uniform: p={our_ks.pvalue:.4f}"
            assert salib_ks.pvalue > 0.01, \
                f"SALib LHS dim {i} not uniform: p={salib_ks.pvalue:.4f}"
    
    def test_lhs_stratification_matches_salib(
        self, reference_salib, n_samples
    ):
        """
        PROPERTY: Our LHS should be stratified like SALib's.
        
        Each stratum [i/n, (i+1)/n] should contain exactly 1 sample per dim.
        """
        from cbms_sim.domain.uq.sampling import lh_sample
        from SALib.sample import latin as salib_latin
        
        n_vars = 4
        problem = {
            'num_vars': n_vars,
            'bounds': [[0, 1]] * n_vars
        }
        
        our_samples = lh_sample(n=n_samples, n_vars=n_vars, seed=42)
        
        salib_samples = salib_latin.sample(problem, n_samples, seed=42)
        
        # Check stratification: each stratum should have exactly 1 sample
        for samples, name in [(our_samples, "our"), (salib_samples, "SALib")]:
            for i in range(n_vars):
                strata_counts = np.zeros(n_samples, dtype=int)
                for j in range(n_samples):
                    stratum_idx = int(samples[j, i] * n_samples)
                    if stratum_idx == n_samples:
                        stratum_idx = n_samples - 1
                    strata_counts[stratum_idx] += 1
                
                assert np.all(strata_counts == 1), \
                    f"{name} LHS dim {i}: stratification violated, max count = {strata_counts.max()}"
    
    def test_lhs_moments_match_salib(self, reference_salib):
        """
        PROPERTY: Our LHS should have similar statistical moments to SALib's.
        """
        from cbms_sim.domain.uq.sampling import lh_sample
        from SALib.sample import latin as salib_latin
        
        n_vars = 3
        n = 1024
        problem = {
            'num_vars': n_vars,
            'bounds': [[0, 1]] * n_vars
        }
        
        our_samples = lh_sample(n=n, n_vars=n_vars, seed=42)
        salib_samples = salib_latin.sample(problem, n, seed=42)
        
        for i in range(n_vars):
            our_moments = compute_sample_moments(our_samples[:, i])
            salib_moments = compute_sample_moments(salib_samples[:, i])
            
            assert abs(our_moments["mean"] - 0.5) < 0.05, \
                f"Our LHS mean for dim {i}: {our_moments['mean']:.4f}"
            assert abs(salib_moments["mean"] - 0.5) < 0.05, \
                f"SALib LHS mean for dim {i}: {salib_moments['mean']:.4f}"
            
            assert abs(our_moments["variance"] - 1/12) < 0.01
            assert abs(salib_moments["variance"] - 1/12) < 0.01
    
    def test_lhs_reproducibility(self):
        """
        PROPERTY: Same seed -> same samples (deterministic).
        """
        from cbms_sim.domain.uq.sampling import lh_sample
        
        s1 = lh_sample(n=100, n_vars=4, seed=42)
        s2 = lh_sample(n=100, n_vars=4, seed=42)
        
        np.testing.assert_array_equal(s1, s2)
