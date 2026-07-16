"""
Property-based tests for uncertainty quantification.
"""

import pytest
import numpy as np
import os

from hypothesis import given, settings
from hypothesis import strategies as st

from cbms_sim.domain.uq.monte_carlo import MonteCarloEngine

# Detect if running in CI
is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("RUN_FULL_FUZZ") == "true"

# =============================================================================
# PARAMETER STRATEGIES FOR UQ
# =========================================================================================

@st.composite
def parameter_specs(draw):
    """Generate valid parameter specifications for MC sampling."""
    n_params = draw(st.integers(min_value=1, max_value=5))
    specs = {}
    for i in range(n_params):
        dist_type = draw(st.sampled_from(["normal", "lognormal", "uniform"]))
        name = f"param_{i}"
        
        if dist_type == "normal":
            specs[name] = {
                "type": "normal",
                "mean": draw(st.floats(0.1, 100, allow_nan=False)),
                "std": draw(st.floats(0.01, 10, allow_nan=False)),
            }
        elif dist_type == "lognormal":
            specs[name] = {
                "type": "lognormal",
                "mean": draw(st.floats(0.1, 100, allow_nan=False)),
                "sigma": draw(st.floats(0.01, 0.5, allow_nan=False)),
            }
        else:
            lo = draw(st.floats(0, 50, allow_nan=False))
            hi = lo + draw(st.floats(0.1, 100, allow_nan=False))
            specs[name] = {
                "type": "uniform",
                "min": lo,
                "max": hi,
            }
    
    return specs


# =========================================================================================
# MONTE CARLO PROPERTIES
# =========================================================================================

class TestMonteCarloProperties:
    """Properties of Monte Carlo sampling."""
    
    @given(specs=parameter_specs(), n=st.integers(min_value=10, max_value=200))
    @settings(max_examples=1000 if is_ci else 50, deadline=30000)
    def test_produces_n_samples(self, specs, n):
        """
        PROPERTY: Monte Carlo with n samples should produce exactly n samples.
        """
        mc = MonteCarloEngine(n_samples=n, seed=42)
        samples = list(mc.generate_samples(specs))
        assert len(samples) == n
    
    @given(specs=parameter_specs(), n=st.integers(min_value=10, max_value=200))
    @settings(max_examples=1000 if is_ci else 50, deadline=60000)
    def test_lognormal_samples_always_positive(self, specs, n):
        """
        PROPERTY: Lognormal samples are always > 0 (by definition).
        """
        for k in specs:
            specs[k] = {"type": "lognormal", "mean": 1.0, "sigma": 0.5}
        
        mc = MonteCarloEngine(n_samples=n, seed=42)
        for sample in mc.generate_samples(specs):
            for name, value in sample.items():
                assert value > 0, f"Lognormal produced non-positive: {value}"
    
    @given(specs=parameter_specs(), n=st.integers(min_value=10, max_value=200))
    @settings(max_examples=1000 if is_ci else 50, deadline=60000)
    def test_uniform_samples_within_bounds(self, specs, n):
        """
        PROPERTY: Uniform samples are within [min, max].
        """
        for k in specs:
            specs[k] = {"type": "uniform", "min": 0.0, "max": 100.0}
        
        mc = MonteCarloEngine(n_samples=n, seed=42)
        for sample in mc.generate_samples(specs):
            for name, value in sample.items():
                assert 0.0 <= value <= 100.0, f"Uniform out of bounds: {value}"
    
    @given(specs=parameter_specs(), n=st.integers(min_value=10, max_value=200))
    @settings(max_examples=200 if is_ci else 20, deadline=60000)
    def test_seed_reproducibility(self, specs, n):
        """
        PROPERTY: Same seed produces same samples (deterministic).
        """
        mc1 = MonteCarloEngine(n_samples=n, seed=42)
        mc2 = MonteCarloEngine(n_samples=n, seed=42)
        
        samples1 = list(mc1.generate_samples(specs))
        samples2 = list(mc2.generate_samples(specs))
        
        for s1, s2 in zip(samples1, samples2):
            for name in s1:
                assert s1[name] == s2[name], f"Sample differs for {name}"
    
    @given(
        spec=st.fixed_dictionaries({
            "type": st.just("normal"),
            "mean": st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
            "std": st.floats(min_value=0.01, max_value=10.0, allow_nan=False),
        }),
        n=st.integers(min_value=1000, max_value=5000),
    )
    @settings(max_examples=200 if is_ci else 20, deadline=60000)
    def test_sample_mean_converges_to_true_mean(self, spec, n):
        """
        PROPERTY: For large n, sample mean approaches true mean.
        """
        mc = MonteCarloEngine(n_samples=n, seed=42)
        samples = [s["x"] for s in mc.generate_samples({"x": spec})]
        
        sample_mean = np.mean(samples)
        rel_err = abs(sample_mean - spec["mean"]) / spec["mean"]
        assert rel_err < 0.15, \
            f"Sample mean {sample_mean} far from true mean {spec['mean']}"
