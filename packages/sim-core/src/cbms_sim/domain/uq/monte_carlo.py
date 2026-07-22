"""
domain/uq/monte_carlo.py
Latin Hypercube Sampling + correlated kinetics parameter Monte Carlo sweeps.

v2 changes:
  - MonteCarloEngine.run() now optionally perturbs kinetic rate constants
    in addition to operational variables (enzyme, temp, flow), via
    CorrelatedKineticsSampler.  Set use_correlated_kinetics=True to enable.
  - Collects nox_pct, pm_pct, metal_pct alongside co2/so2.
  - Statistics dict extended to include all 5 capture outputs.
  - generate_samples() unchanged (used by Sobol engine).
"""

from __future__ import annotations

from typing import Dict, Any, List
import numpy as np
from scipy.stats import qmc

from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsEngine as KineticsEngine, ExtendedKineticsConfig
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.models.results import UQResult
from cbms_sim.domain.uq.correlated_sampler import CorrelatedKineticsSampler, DEFAULT_MARGINALS
from cbms_shared.exceptions import UQConvergenceError
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class MonteCarloEngine:
    """
    Executes LHS simulation runs over operational and kinetic parameter variance.

    Two modes:
      use_correlated_kinetics=False (default):
        Perturbs enzyme, temperature, and flow ±20% with independent LHS.
        Fast, suitable for operational sensitivity.

      use_correlated_kinetics=True:
        Additionally perturbs all 9 kinetic rate constants using the Gaussian-copula
        sampler — captures physical correlations (k_cat↔thermal stability, etc.)
        that independent sampling misses.  ~2× slower (extra ODE solves per sample).
    """

    def __init__(
        self,
        n_samples: int = 30,
        seed: int = 42,
        use_correlated_kinetics: bool = False,
    ) -> None:
        self.n_samples = n_samples
        self.seed = seed
        self.use_correlated_kinetics = use_correlated_kinetics

    def run(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions,
    ) -> UQResult:
        """Run Monte Carlo uncertainty sweep over operational variables."""
        enzyme = float(reagent.enzyme_mg_per_l)
        temp   = float(conditions.reactor_temp_c)
        flow   = float(plant.exhaust_flow_nm3_hr)

        bounds_lower = np.array([
            max(1.0,     enzyme * 0.8),
            max(20.0,    temp   * 0.8),
            max(1000.0,  flow   * 0.8),
        ])
        bounds_upper = np.array([
            min(50.0,    enzyme * 1.2),
            min(65.0,    temp   * 1.2),
            min(20000.0, flow   * 1.2),
        ])

        # Saltelli design for Sobol sensitivity analysis
        n_vars = 3
        step   = n_vars + 2
        N      = max(1, self.n_samples // step)

        sampler   = qmc.LatinHypercube(d=n_vars, seed=self.seed)
        points_A  = sampler.random(n=N)
        sampler_B = qmc.LatinHypercube(d=n_vars, seed=self.seed + 1)
        points_B  = sampler_B.random(n=N)

        scaled_A = qmc.scale(points_A, bounds_lower, bounds_upper)
        scaled_B = qmc.scale(points_B, bounds_lower, bounds_upper)

        scaled_samples = []
        for j in range(N):
            scaled_samples.append(scaled_A[j])
            for i in range(n_vars):
                row_ab    = np.copy(scaled_A[j])
                row_ab[i] = scaled_B[j][i]
                scaled_samples.append(row_ab)
            scaled_samples.append(scaled_B[j])

        scaled_samples = np.array(scaled_samples)
        n_total = len(scaled_samples)

        # Optionally draw correlated kinetics perturbations
        kinetics_draws: dict[str, np.ndarray] | None = None
        if self.use_correlated_kinetics:
            kin_sampler    = CorrelatedKineticsSampler(n_samples=n_total, seed=self.seed)
            kinetics_draws = kin_sampler.draw()

        engine = KineticsEngine()
        engine.warmup()

        co2_effs   = []
        so2_effs   = []
        nox_effs   = []
        pm_effs    = []
        metal_effs = []

        for idx, sample in enumerate(scaled_samples):
            e_val, t_val, f_val = sample

            p_sample = PlantProfile(
                name=plant.name,
                location=plant.location,
                boiler_type=plant.boiler_type,
                exhaust_flow_nm3_hr=type(plant.exhaust_flow_nm3_hr)(f_val),
                co2_vol_pct=plant.co2_vol_pct,
                so2_mg_per_nm3=plant.so2_mg_per_nm3,
            )
            r_sample = ReagentFormulation(
                chitosan_wt_pct=reagent.chitosan_wt_pct,
                enzyme_mg_per_l=type(reagent.enzyme_mg_per_l)(e_val),
            )
            c_sample = OperatingConditions(
                reactor_temp_c=type(conditions.reactor_temp_c)(t_val),
            )

            # Override solver params if correlated kinetics are enabled
            if kinetics_draws is not None:
                k_config = _make_perturbed_config(kinetics_draws, idx)
                local_engine = KineticsEngine(config=k_config)
                local_engine._warmed_up = True  # skip warmup, config already set
            else:
                local_engine = engine

            try:
                res         = local_engine.solve(p_sample, r_sample, c_sample)
                effs        = res.capture_efficiencies
                co2_effs.append(effs.get("co2_pct",   0.0))
                so2_effs.append(effs.get("so2_pct",   0.0))
                nox_effs.append(effs.get("nox_pct",   0.0))
                pm_effs.append(effs.get("pm_pct",     0.0))
                metal_effs.append(effs.get("metal_pct", 0.0))
            except Exception as exc:
                logger.warning("MC sample %d failed: %s — skipping", idx, exc)
                # Carry forward previous value or 0.0 so array lengths stay aligned
                for arr in (co2_effs, so2_effs, nox_effs, pm_effs, metal_effs):
                    arr.append(arr[-1] if arr else 0.0)

        def _stats(arr: list) -> dict:
            a = np.array(arr)
            return {
                "mean": float(np.mean(a)),
                "std":  float(np.std(a)),
                "p05":  float(np.percentile(a, 5)),
                "p95":  float(np.percentile(a, 95)),
                "samples": arr,
            }

        statistics = {
            "co2":   _stats(co2_effs),
            "so2":   _stats(so2_effs),
            "nox":   _stats(nox_effs),
            "pm":    _stats(pm_effs),
            "metal": _stats(metal_effs),
        }

        return UQResult(
            samples=scaled_samples,
            statistics=statistics,
            diagnostics={
                "n_samples":             len(scaled_samples),
                "correlated_kinetics":   self.use_correlated_kinetics,
            },
            outputs={
                "co2_pct":   np.array(co2_effs),
                "so2_pct":   np.array(so2_effs),
                "nox_pct":   np.array(nox_effs),
                "pm_pct":    np.array(pm_effs),
                "metal_pct": np.array(metal_effs),
            },
        )

    def generate_samples(self, specs: Dict[str, Dict[str, Any]]) -> List[Dict[str, float]]:
        """Generate samples matching given parameter specifications using LHS."""
        from scipy.stats import norm, lognorm, uniform

        sampler = qmc.LatinHypercube(d=len(specs), seed=self.seed)
        points  = sampler.random(n=self.n_samples)

        results = [{} for _ in range(self.n_samples)]
        for idx, (name, spec) in enumerate(specs.items()):
            col       = points[:, idx]
            dist_type = spec["type"]
            if dist_type == "normal":
                values = norm.ppf(col, loc=spec["mean"], scale=spec["std"])
            elif dist_type == "lognormal":
                s      = spec.get("sigma", 0.5)
                mu     = np.log(spec["mean"]) - 0.5 * (s ** 2)
                values = lognorm.ppf(col, s=s, scale=np.exp(mu))
            elif dist_type == "uniform":
                loc    = spec["min"]
                values = uniform.ppf(col, loc=loc, scale=spec["max"] - loc)
            else:
                values = col

            for row_idx, val in enumerate(values):
                results[row_idx][name] = float(val)

        return results


def _make_perturbed_config(draws: dict[str, np.ndarray], idx: int) -> ExtendedKineticsConfig:
    """
    Build an ExtendedKineticsConfig with perturbed rate constants for sample `idx`.
    Rate constants are injected into solver_params via config.rate_overrides.
    """
    rate_overrides = {key: float(values[idx]) for key, values in draws.items()}
    logger.debug(
        "Correlated kinetics perturbation at sample %d: k_cat=%.3e, k_so2=%.3e",
        idx,
        rate_overrides.get("k_cat", 1e6),
        rate_overrides.get("k_so2_abs", 2.5e-2),
    )
    return ExtendedKineticsConfig(rate_overrides=rate_overrides)
