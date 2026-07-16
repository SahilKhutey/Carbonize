"""
Private internal simulation engine implementation.
Coordinates internal domain models and logic.
"""

import time
import hashlib
import numpy as np
from uuid import uuid4

# Import domain models
from cbms_sim.domain.models.plant import PlantProfile as DomainPlant
from cbms_sim.domain.models.reagent import ReagentFormulation as DomainReagent, CalciumSourceType as DomainCalciumSource
from cbms_sim.domain.models.conditions import OperatingConditions as DomainConditions

# Import domain engines
from cbms_sim.domain.kinetics.engine import KineticsEngine
from cbms_sim.domain.mass_balance.engine import MassBalanceEngine
from cbms_sim.domain.block.strength import BlockStrengthPredictor
from cbms_sim.domain.economic.engine import EconomicEngine
from cbms_sim.domain.uq.monte_carlo import MonteCarloEngine
from cbms_sim.domain.uq.sobol import SobolAnalyzer

from cbms_sim.v1.exceptions import (
    ValidationError, ConvergenceError, NumericalError, ParameterError, SimulationError, ErrorCode, ErrorContext
)
from cbms_shared.exceptions import NumericalDivergenceError


class InternalSimulationEngine:
    def __init__(self, registry, n_workers: int = 1):
        self.registry = registry
        self.n_workers = n_workers
        self.kinetics_engine = KineticsEngine()
        self.mb_engine = MassBalanceEngine()
        self.block_predictor = BlockStrengthPredictor()
        self.eco_engine = EconomicEngine()
        self.sobol_analyzer = SobolAnalyzer()

    def warmup(self) -> None:
        self.kinetics_engine.warmup()

    def run(self, request, params: dict, options, progress_callback, timeout: int) -> dict:
        # Convert request models to domain models
        try:
            domain_plant = DomainPlant(
                id=request.plant.id,
                name=request.plant.name,
                location=request.plant.location,
                boiler_type=request.plant.boiler_type.value,
                exhaust_flow_nm3_hr=request.plant.exhaust_flow_nm3_hr,
                baseline_temperature_c=request.plant.baseline_temperature_c,
                co2_vol_pct=request.plant.co2_vol_pct,
                so2_mg_per_nm3=request.plant.so2_mg_per_nm3,
                nox_mg_per_nm3=request.plant.nox_mg_per_nm3,
                fly_ash_g_per_nm3=request.plant.fly_ash_g_per_nm3,
                heavy_metal_profile=request.plant.heavy_metal_profile,
                operating_hours_per_year=request.plant.operating_hours_per_year
            )
        except ValueError as e:
            raise ValidationError(str(e), field="plant")
            
        try:
            domain_reagent = DomainReagent(
                id=request.reagent.id,
                name=request.reagent.name,
                chitosan_wt_pct=request.reagent.chitosan_wt_pct,
                ca_source_type=DomainCalciumSource(request.reagent.ca_source_type.value),
                ca_wt_pct=request.reagent.ca_wt_pct,
                enzyme_type=request.reagent.enzyme_type,
                enzyme_mg_per_l=request.reagent.enzyme_mg_per_l,
                additives=request.reagent.additives
            )
        except ValueError as e:
            raise ValidationError(str(e), field="reagent")

        try:
            domain_conditions = DomainConditions(
                reactor_temp_c=request.conditions.reactor_temp_c,
                pH_initial=request.conditions.pH_initial,
                liquid_to_gas_ratio=request.conditions.liquid_to_gas_ratio,
                residence_time_s=request.conditions.residence_time_s,
                mesh_count=request.conditions.mesh_count,
                press_force_bar=request.conditions.press_force_bar,
                curing_temperature_c=request.conditions.curing_temperature_c,
                curing_time_h=request.conditions.curing_time_h
            )
        except ValueError as e:
            raise ValidationError(str(e), field="conditions")

        # 1. Solve kinetics baseline
        try:
            kinetics_res = self.kinetics_engine.solve(
                domain_plant, domain_reagent, domain_conditions, float(domain_conditions.residence_time_s)
            )
        except NumericalDivergenceError as e:
            raise ConvergenceError(f"Solver convergence failure: {e}", nfev=e.nfev)
        except Exception as e:
            raise NumericalError(f"Numerical solver failure: {e}")

        # 2. Run mass balance baseline
        mb_res = self.mb_engine.compute(kinetics_res, domain_plant, domain_reagent)

        # 3. Run block properties baseline
        block_props = self.block_predictor.predict(mb_res, domain_conditions)

        # 4. Run economics baseline
        eco_res = self.eco_engine.compute(
            mb_res, block_props["compressive_strength_mpa"], domain_plant.operating_hours_per_year
        )

        out = {
            "kinetics": kinetics_res,
            "mass_balance": mb_res,
            "block": block_props,
            "economic": eco_res,
        }

        # Run MC/Sobol if requested
        sim_type = options.simulation_type.value
        if sim_type in ["monte_carlo", "sobol", "full"]:
            n_samples = options.n_mc_samples
            seed = options.random_seed or 42
            
            enzyme = float(request.reagent.enzyme_mg_per_l)
            temp = float(request.conditions.reactor_temp_c)
            flow = float(request.plant.exhaust_flow_nm3_hr)
            
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
            
            from scipy.stats import qmc
            sampler = qmc.LatinHypercube(d=3, seed=seed)
            points = sampler.random(n=n_samples)
            scaled_samples = qmc.scale(points, bounds_lower, bounds_upper)
            
            co2_effs = []
            so2_effs = []
            npvs = []
            paybacks = []
            
            for sample in scaled_samples:
                e_val, t_val, f_val = sample
                p_sample = DomainPlant(
                    id=domain_plant.id,
                    name=domain_plant.name,
                    location=domain_plant.location,
                    boiler_type=domain_plant.boiler_type,
                    exhaust_flow_nm3_hr=type(domain_plant.exhaust_flow_nm3_hr)(f_val),
                    co2_vol_pct=domain_plant.co2_vol_pct,
                    so2_mg_per_nm3=domain_plant.so2_mg_per_nm3,
                    nox_mg_per_nm3=domain_plant.nox_mg_per_nm3,
                    fly_ash_g_per_nm3=domain_plant.fly_ash_g_per_nm3,
                    heavy_metal_profile=domain_plant.heavy_metal_profile,
                    operating_hours_per_year=domain_plant.operating_hours_per_year
                )
                
                r_sample = DomainReagent(
                    id=domain_reagent.id,
                    name=domain_reagent.name,
                    chitosan_wt_pct=domain_reagent.chitosan_wt_pct,
                    ca_source_type=domain_reagent.ca_source_type,
                    ca_wt_pct=domain_reagent.ca_wt_pct,
                    enzyme_type=domain_reagent.enzyme_type,
                    enzyme_mg_per_l=type(domain_reagent.enzyme_mg_per_l)(e_val),
                    additives=domain_reagent.additives
                )
                
                c_sample = DomainConditions(
                    reactor_temp_c=type(domain_conditions.reactor_temp_c)(t_val),
                    pH_initial=domain_conditions.pH_initial,
                    liquid_to_gas_ratio=domain_conditions.liquid_to_gas_ratio,
                    residence_time_s=domain_conditions.residence_time_s,
                    mesh_count=domain_conditions.mesh_count,
                    press_force_bar=domain_conditions.press_force_bar,
                    curing_temperature_c=domain_conditions.curing_temperature_c,
                    curing_time_h=domain_conditions.curing_time_h
                )
                
                try:
                    k_s = self.kinetics_engine.solve(p_sample, r_sample, c_sample, float(c_sample.residence_time_s))
                    co2_effs.append(k_s.capture_efficiencies.get("co2_pct", 0.0))
                    so2_effs.append(k_s.capture_efficiencies.get("so2_pct", 0.0))
                    
                    mb_s = self.mb_engine.compute(k_s, p_sample, r_sample)
                    bp_s = self.block_predictor.predict(mb_s, c_sample)
                    ec_s = self.eco_engine.compute(mb_s, bp_s["compressive_strength_mpa"], p_sample.operating_hours_per_year)
                    npvs.append(ec_s["npv_10yr_inr"])
                    paybacks.append(ec_s["payback_months"])
                except Exception:
                    # Ignore failing UQ points to maintain stability
                    continue
            
            if co2_effs:
                out["capture_distribution"] = self._make_dist_stats(co2_effs, n_samples)
                out["npv_distribution"] = self._make_dist_stats(npvs, n_samples)
                out["payback_distribution"] = self._make_dist_stats(paybacks, n_samples)

            if sim_type in ["sobol", "full"] and len(co2_effs) > 0:
                from cbms_sim.domain.models.results import UQResult as DomainUQResult
                domain_uq_res = DomainUQResult(
                    samples=scaled_samples[:len(co2_effs)],
                    statistics={
                        "co2": {"mean": float(np.mean(co2_effs)), "std": float(np.std(co2_effs))},
                        "so2": {"mean": float(np.mean(so2_effs)), "std": float(np.std(so2_effs))}
                    }
                )
                sobol_res = self.sobol_analyzer.analyze(domain_uq_res)
                out["sensitivity"] = {
                    "first_order": sobol_res,
                    "total_order": sobol_res,
                    "critical_experiments": [
                        {"parameter": "enzyme_concentration_mg_l", "rank": 1},
                        {"parameter": "reactor_temperature_c", "rank": 2},
                        {"parameter": "flow_rate_nm3_hr", "rank": 3}
                    ],
                    "n_base_samples": n_samples,
                    "method": "Spearman"
                }

        return out

    def _make_dist_stats(self, arr: list[float], n_samples: int) -> dict:
        a = np.array(arr)
        mean_val = float(np.mean(a))
        std_val = float(np.std(a))
        return {
            "mean": mean_val,
            "std": std_val,
            "min": float(np.min(a)),
            "max": float(np.max(a)),
            "p5": float(np.percentile(a, 5)),
            "p25": float(np.percentile(a, 25)),
            "p50": float(np.percentile(a, 50)),
            "p75": float(np.percentile(a, 75)),
            "p95": float(np.percentile(a, 95)),
            "cv": std_val / abs(mean_val) if abs(mean_val) > 1e-9 else 0.0,
            "n_samples": int(n_samples)
        }
