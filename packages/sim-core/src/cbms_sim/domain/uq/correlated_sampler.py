"""
domain/uq/correlated_sampler.py
Correlated Monte Carlo sampler using a Gaussian copula.

Motivation:
  Rate constants are NOT independent — enzyme catalytic turnover (k_cat) and
  thermal inactivation rate (ca_inactivation) share the same protein structure,
  so high k_cat tends to co-occur with higher thermal sensitivity.  Similarly,
  SO₂ and NOx absorption coefficients are correlated through the alkalinity budget.

  Independent uniform sampling (as in monte_carlo.py) over-disperses the joint
  distribution and can generate physically impossible combinations.  A Gaussian
  copula maps marginal distributions through a multivariate normal with a
  calibrated correlation matrix, respecting those dependencies.

Usage::

    sampler = CorrelatedKineticsSampler(n_samples=500, seed=42)
    samples = sampler.draw()   # dict[str, np.ndarray]

Each value is an array of n_samples draws for that parameter.
"""

from __future__ import annotations

import numpy as np
from scipy import stats
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MarginalSpec:
    """Specification for a single parameter's marginal distribution."""
    name: str
    dist: str          # "uniform" | "normal" | "lognormal" | "beta"
    params: dict[str, float] = field(default_factory=dict)

    def ppf(self, u: np.ndarray) -> np.ndarray:
        """Percent-point function (inverse CDF) — maps U[0,1] → marginal."""
        if self.dist == "uniform":
            return stats.uniform.ppf(u, loc=self.params["low"],
                                     scale=self.params["high"] - self.params["low"])
        elif self.dist == "normal":
            return stats.norm.ppf(u, loc=self.params["mean"], scale=self.params["std"])
        elif self.dist == "lognormal":
            # parameterised as (mean, std) of the *underlying* normal
            return stats.lognorm.ppf(u, s=self.params["sigma"],
                                     scale=np.exp(self.params["mu"]))
        elif self.dist == "beta":
            return stats.beta.ppf(u, a=self.params["a"], b=self.params["b"],
                                  loc=self.params.get("loc", 0.0),
                                  scale=self.params.get("scale", 1.0))
        else:
            raise ValueError(f"Unknown distribution: {self.dist}")


# ---------------------------------------------------------------------------
# Default kinetics parameter marginals
# ---------------------------------------------------------------------------
# Literature-derived ±20 % uncertainty unless noted.
# Lognormal parameterisation: mu/sigma are the mean/std of ln(X).

def _lognorm_params(mean: float, cv: float) -> dict[str, float]:
    """Convert (mean, coefficient of variation) to lognormal mu/sigma."""
    sigma = np.sqrt(np.log(1 + cv**2))
    mu    = np.log(mean) - 0.5 * sigma**2
    return {"mu": mu, "sigma": sigma}


DEFAULT_MARGINALS: list[MarginalSpec] = [
    MarginalSpec("k_cat",           "lognormal", _lognorm_params(1.0e6, 0.20)),
    MarginalSpec("K_M_co2",         "lognormal", _lognorm_params(8.5,   0.15)),
    MarginalSpec("K_i_hco3",        "lognormal", _lognorm_params(26.0,  0.15)),
    MarginalSpec("k_so2_abs",       "lognormal", _lognorm_params(2.5e-2, 0.25)),
    MarginalSpec("k_no2_abs",       "lognormal", _lognorm_params(1.0e-2, 0.30)),
    MarginalSpec("k_precip_caco3",  "lognormal", _lognorm_params(1.5e-2, 0.20)),
    MarginalSpec("k_chel",          "lognormal", _lognorm_params(8.0e-3, 0.25)),
    MarginalSpec("ca_inactivation", "lognormal", _lognorm_params(5.0e-5, 0.30)),
    MarginalSpec("E_a_inact",       "normal",    {"mean": 85.0e3, "std": 5.0e3}),
]


# ---------------------------------------------------------------------------
# Correlation matrix (Pearson on the Gaussian copula scale)
# ---------------------------------------------------------------------------
# Rows/cols map 1:1 to DEFAULT_MARGINALS order.
# k_cat ↔ ca_inactivation: +0.45  (faster enzymes are more thermally sensitive)
# k_so2_abs ↔ k_no2_abs:   +0.60  (both depend on alkalinity sink)
# k_cat ↔ E_a_inact:       +0.30  (higher activation energy → more temperature-sensitive)
# All others treated as independent (off-diagonal = 0).

def _build_default_corr() -> np.ndarray:
    n = len(DEFAULT_MARGINALS)
    idx = {m.name: i for i, m in enumerate(DEFAULT_MARGINALS)}
    C = np.eye(n)
    pairs = [
        ("k_cat",     "ca_inactivation", 0.45),
        ("k_so2_abs", "k_no2_abs",       0.60),
        ("k_cat",     "E_a_inact",        0.30),
        ("k_cat",     "K_M_co2",         -0.25),  # faster cat. → lower apparent Km
    ]
    for a, b, r in pairs:
        i, j = idx[a], idx[b]
        C[i, j] = C[j, i] = r
    return C


DEFAULT_CORR = _build_default_corr()


class CorrelatedKineticsSampler:
    """
    Gaussian-copula sampler for kinetic rate constants.

    Algorithm:
      1. Draw Z ~ MVN(0, Σ) where Σ is the correlation matrix
      2. Map each dimension through the standard-normal CDF: U = Φ(Z) → U[0,1]
      3. Map U through each marginal's inverse CDF (PPF): X = F⁻¹(U)

    This preserves the prescribed Pearson correlations in the copula space
    while honouring arbitrary marginal distributions.
    """

    def __init__(
        self,
        n_samples: int = 500,
        seed: int = 42,
        marginals: list[MarginalSpec] | None = None,
        corr: np.ndarray | None = None,
    ) -> None:
        self.n_samples = n_samples
        self.rng = np.random.default_rng(seed)
        self.marginals = marginals or DEFAULT_MARGINALS
        self.corr = corr if corr is not None else DEFAULT_CORR

        # Validate and regularise correlation matrix
        n = len(self.marginals)
        assert self.corr.shape == (n, n), "corr must be (n_params, n_params)"
        # Ensure positive definiteness via nearest-PD projection
        self.corr = _nearest_pd(self.corr)

    def draw(self) -> dict[str, np.ndarray]:
        """
        Draw n_samples correlated parameter vectors.
        Returns {param_name: array(n_samples)} for each marginal.
        """
        n = len(self.marginals)
        # Step 1: Draw from multivariate normal
        L = np.linalg.cholesky(self.corr)
        Z = self.rng.standard_normal((self.n_samples, n)) @ L.T

        # Step 2: Convert to uniform marginals via standard-normal CDF
        U = stats.norm.cdf(Z)  # shape (n_samples, n)

        # Step 3: Map through each marginal's PPF
        result: dict[str, np.ndarray] = {}
        for j, marginal in enumerate(self.marginals):
            result[marginal.name] = marginal.ppf(U[:, j])

        return result

    def draw_dataframe(self) -> "Any":
        """Return samples as a pandas DataFrame (optional convenience)."""
        try:
            import pandas as pd
            return pd.DataFrame(self.draw())
        except ImportError:
            raise ImportError("pandas is required for draw_dataframe()")


def _nearest_pd(A: np.ndarray) -> np.ndarray:
    """
    Find the nearest positive-definite matrix to A (Higham 1988).
    Ensures the correlation matrix remains PD after user edits.
    """
    B = (A + A.T) / 2
    _, s, V = np.linalg.svd(B)
    H = V.T @ np.diag(s) @ V
    A2 = (B + H) / 2
    A3 = (A2 + A2.T) / 2

    if _is_pd(A3):
        return A3

    spacing = np.spacing(np.linalg.norm(A))
    I = np.eye(A.shape[0])
    k = 1
    while not _is_pd(A3):
        min_eig = np.min(np.real(np.linalg.eigvals(A3)))
        A3 += I * (-min_eig * k**2 + spacing)
        k += 1
    return A3


def _is_pd(B: np.ndarray) -> bool:
    try:
        np.linalg.cholesky(B)
        return True
    except np.linalg.LinAlgError:
        return False
