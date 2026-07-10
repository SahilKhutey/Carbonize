"""
domain/uq/monte_carlo.py
Implements Latin Hypercube Sampling (LHS) and parallel forward uncertainty evaluations.
"""

from typing import Dict, Any, List
import numpy as np
from scipy.stats import qmc
from cbms_sim.domain.kinetics.engine import solve_kinetics
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.models.results import UQResult
from cbms_shared.exceptions import UQConvergenceError
from cbms_shared.logging import get_logger

logger = get_logger(__name__)

class MonteCarloEngine:
    """Executes LHS simulation runs over parameter variance envelopes."""
    
    def __init__(self, n_samples: int = 30, seed: int = 42) -> None:
        self.n_samples = n_samples
        self.seed = seed
        
    def run(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions
    ) -> UQResult:
        """Run LHS uncertainty evaluations across enzyme, temperature, and flow rate bounds."""
        # bounds: mean +/- 20%
        enzyme = float(reagent.enzyme_mg_per_l)
        temp = float(conditions.reactor_temp_c)
        flow = float(plant.exhaust_flow_nm3_hr)
        
        bounds_lower = np.array([
            max(1.0, enzyme * 0.8),
            max(20.0, temp * 0.8),
            max(1000.0, flow * 0.8)
        ])
        bounds_upper = np.array([
            min(50.0, enzyme * 1.2),
            min(65.0, temp * 1.2),
            min(20000.0, flow * 1.2)
        ])
        
        sampler = qmc.LatinHypercube(d=3, seed=self.seed)
        points = sampler.random(n=self.n_samples)
        scaled_samples = qmc.scale(points, bounds_lower, bounds_upper)
        
        co2_effs = []
        so2_effs = []
        
        for sample in scaled_samples:
            e_val, t_val, f_val = sample
            
            p_sample = PlantProfile(
                name=plant.name,
                location=plant.location,
                boiler_type=plant.boiler_type,
                exhaust_flow_nm3_hr=type(plant.exhaust_flow_nm3_hr)(f_val),
                co2_vol_pct=plant.co2_vol_pct,
                so2_mg_per_nm3=plant.so2_mg_per_nm3
            )
            
            r_sample = ReagentFormulation(
                chitosan_wt_pct=reagent.chitosan_wt_pct,
                enzyme_mg_per_l=type(reagent.enzyme_mg_per_l)(e_val)
            )
            
            c_sample = OperatingConditions(
                reactor_temp_c=type(conditions.reactor_temp_c)(t_val)
            )
            
            res = solve_kinetics(p_sample, r_sample, c_sample)
            co2_effs.append(res.capture_efficiencies.get("co2_pct", 0.0))
            so2_effs.append(res.capture_efficiencies.get("so2_pct", 0.0))
            
        co2_arr = np.array(co2_effs)
        so2_arr = np.array(so2_effs)
        
        statistics = {
            "co2": {
                "mean": float(np.mean(co2_arr)),
                "std": float(np.std(co2_arr)),
                "p05": float(np.percentile(co2_arr, 5)),
                "p95": float(np.percentile(co2_arr, 95))
            },
            "so2": {
                "mean": float(np.mean(so2_arr)),
                "std": float(np.std(so2_arr))
            }
        }
        
        return UQResult(
            samples=scaled_samples,
            statistics=statistics,
            diagnostics={"n_samples": self.n_samples}
        )
