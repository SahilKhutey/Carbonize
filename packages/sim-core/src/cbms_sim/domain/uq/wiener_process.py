"""
domain/uq/wiener_process.py
Monte Carlo simulation of liquid matrix saturation using Wiener process.
Computes First Passage Time distribution for predictive maintenance scheduling.
"""

import numpy as np
from scipy.stats import invgauss
from dataclasses import dataclass
from typing import Tuple


@dataclass
class WienerResult:
    """Output of the stochastic saturation analysis."""
    mean_fpt_hours: float
    median_fpt_hours: float
    p95_fpt_hours: float
    p5_fpt_hours: float
    saturation_within_window_pct: float
    valid_runs: int
    total_runs: int


def simulate_saturation_fpt(
    drift_mu_kg_hr: float,
    volatility_sigma_kg_hr: float,
    capacity_threshold_kg: float,
    observation_window_hr: float = 24.0,
    time_step_hr: float = 0.01,
    num_paths: int = 5000,
    seed: int = 42,
) -> Tuple[np.ndarray, WienerResult]:
    """
    Simulate cumulative pollutant mass accumulation via Euler-Maruyama
    discretization of the Wiener process with drift.

    Returns:
        (paths, summary_statistics)
    """
    rng = np.random.default_rng(seed)
    num_steps = int(observation_window_hr / time_step_hr)
    time_grid = np.linspace(0, observation_window_hr, num_steps)

    # Vectorized generation of all increments
    dW = rng.normal(0.0, np.sqrt(time_step_hr), size=(num_steps - 1, num_paths))
    paths = np.zeros((num_steps, num_paths))
    paths[0] = 0.0

    # Sequential accumulation
    for t in range(1, num_steps):
        paths[t] = paths[t - 1] + drift_mu_kg_hr * time_step_hr + volatility_sigma_kg_hr * dW[t - 1]

    # First Passage Time (FPT) calculation
    crossed = paths >= capacity_threshold_kg
    fpt = np.full(num_paths, np.nan)
    cross_indices = np.argmax(crossed, axis=0)
    any_crossed = crossed.any(axis=0)
    fpt[any_crossed] = time_grid[cross_indices[any_crossed]]

    valid_fpts = fpt[~np.isnan(fpt)]
    saturation_rate = (len(valid_fpts) / num_paths) * 100.0

    if len(valid_fpts) > 0:
        summary = WienerResult(
            mean_fpt_hours=float(np.mean(valid_fpts)),
            median_fpt_hours=float(np.median(valid_fpts)),
            p95_fpt_hours=float(np.percentile(valid_fpts, 95)),
            p5_fpt_hours=float(np.percentile(valid_fpts, 5)),
            saturation_within_window_pct=saturation_rate,
            valid_runs=len(valid_fpts),
            total_runs=num_paths,
        )
    else:
        summary = WienerResult(
            mean_fpt_hours=observation_window_hr,
            median_fpt_hours=observation_window_hr,
            p95_fpt_hours=observation_window_hr,
            p5_fpt_hours=observation_window_hr,
            saturation_within_window_pct=0.0,
            valid_runs=0,
            total_runs=num_paths,
        )

    return paths, summary


def predict_saturation_window(
    drift_mu: float,
    volatility_sigma: float,
    capacity_kg: float,
    confidence: float = 0.95,
) -> float:
    """
    Compute the theoretical first-passage time using the Inverse Gaussian
    distribution. Used for fast analytical estimates without Monte Carlo.

    Returns:
        Estimated hours to reach saturation at the given confidence level.
    """
    if drift_mu <= 0 or capacity_kg <= 0:
        return float("inf")

    mean_fpt = capacity_kg / drift_mu
    shape_param = (capacity_kg ** 2) / (volatility_sigma ** 2)

    # Use inverse CDF for confidence quantile
    quantile = invgauss.ppf(confidence, shape_param / mean_fpt, scale=mean_fpt)
    return float(quantile)
