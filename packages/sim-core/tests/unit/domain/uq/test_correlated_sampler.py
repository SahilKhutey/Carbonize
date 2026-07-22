"""
tests/unit/domain/uq/test_correlated_sampler.py
Unit tests for the Gaussian-copula correlated kinetics sampler.
"""

import numpy as np
import pytest
from cbms_sim.domain.uq.correlated_sampler import (
    CorrelatedKineticsSampler,
    DEFAULT_MARGINALS,
    DEFAULT_CORR,
    MarginalSpec,
    _nearest_pd,
    _is_pd,
)


class TestMarginalSpec:
    def test_uniform_ppf(self):
        m = MarginalSpec("x", "uniform", {"low": 0.0, "high": 10.0})
        assert m.ppf(np.array([0.0]))[0] == pytest.approx(0.0, abs=1e-9)
        assert m.ppf(np.array([1.0]))[0] == pytest.approx(10.0, abs=1e-3)
        assert m.ppf(np.array([0.5]))[0] == pytest.approx(5.0, abs=1e-6)

    def test_normal_ppf(self):
        m = MarginalSpec("x", "normal", {"mean": 0.0, "std": 1.0})
        assert m.ppf(np.array([0.5]))[0] == pytest.approx(0.0, abs=1e-6)

    def test_lognormal_ppf_positive(self):
        m = MarginalSpec("x", "lognormal", {"mu": 0.0, "sigma": 0.2})
        samples = m.ppf(np.linspace(0.01, 0.99, 50))
        assert np.all(samples > 0)

    def test_unknown_dist_raises(self):
        m = MarginalSpec("x", "pareto", {"a": 1.0})
        with pytest.raises(ValueError, match="Unknown distribution"):
            m.ppf(np.array([0.5]))


class TestNearestPD:
    def test_already_pd_unchanged(self):
        A = np.eye(3)
        B = _nearest_pd(A)
        assert _is_pd(B)

    def test_non_pd_corrected(self):
        # Correlation matrix with invalid entry (eigenvalue < 0)
        A = np.array([[1.0, 0.9, 0.9],
                      [0.9, 1.0, 0.9],
                      [0.9, 0.9, 1.0]])
        # This is actually PD but try a bad one:
        B = np.array([[1.0, 1.0],
                      [1.0, 1.0]])  # singular
        C = _nearest_pd(B)
        assert _is_pd(C)


class TestDefaultCorr:
    def test_correlation_matrix_is_pd(self):
        """Default correlation matrix must be positive definite."""
        assert _is_pd(DEFAULT_CORR)

    def test_diagonal_is_ones(self):
        np.testing.assert_array_almost_equal(np.diag(DEFAULT_CORR), 1.0)

    def test_symmetric(self):
        np.testing.assert_array_almost_equal(DEFAULT_CORR, DEFAULT_CORR.T)

    def test_k_cat_ca_inact_positive_correlation(self):
        """k_cat ↔ ca_inactivation should be positively correlated (0.45)."""
        names = [m.name for m in DEFAULT_MARGINALS]
        i = names.index("k_cat")
        j = names.index("ca_inactivation")
        assert DEFAULT_CORR[i, j] == pytest.approx(0.45, abs=1e-9)

    def test_so2_no2_positive_correlation(self):
        names = [m.name for m in DEFAULT_MARGINALS]
        i = names.index("k_so2_abs")
        j = names.index("k_no2_abs")
        assert DEFAULT_CORR[i, j] == pytest.approx(0.60, abs=1e-9)


class TestSampler:
    @pytest.fixture
    def sampler(self):
        return CorrelatedKineticsSampler(n_samples=200, seed=0)

    def test_draw_returns_all_params(self, sampler):
        samples = sampler.draw()
        assert set(samples.keys()) == {m.name for m in DEFAULT_MARGINALS}

    def test_draw_correct_shape(self, sampler):
        samples = sampler.draw()
        for arr in samples.values():
            assert arr.shape == (200,)

    def test_k_cat_positive(self, sampler):
        """All k_cat samples must be positive (lognormal)."""
        samples = sampler.draw()
        assert np.all(samples["k_cat"] > 0)

    def test_empirical_correlation_close_to_specified(self, sampler):
        """Empirical Pearson correlation should approximate the specified value."""
        large_sampler = CorrelatedKineticsSampler(n_samples=5000, seed=42)
        s = large_sampler.draw()

        names = [m.name for m in DEFAULT_MARGINALS]
        i = names.index("k_so2_abs")
        j = names.index("k_no2_abs")

        # Correlation in log-space (lognormals) should be close to 0.60
        corr = np.corrcoef(np.log(s["k_so2_abs"]), np.log(s["k_no2_abs"]))[0, 1]
        assert abs(corr - 0.60) < 0.08, f"Expected ~0.60 but got {corr:.3f}"

    def test_reprodicible_with_same_seed(self):
        a = CorrelatedKineticsSampler(n_samples=50, seed=7).draw()
        b = CorrelatedKineticsSampler(n_samples=50, seed=7).draw()
        np.testing.assert_array_equal(a["k_cat"], b["k_cat"])

    def test_different_seeds_differ(self):
        a = CorrelatedKineticsSampler(n_samples=50, seed=1).draw()
        b = CorrelatedKineticsSampler(n_samples=50, seed=2).draw()
        assert not np.allclose(a["k_cat"], b["k_cat"])
