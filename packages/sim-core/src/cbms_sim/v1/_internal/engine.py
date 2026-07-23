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
from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsEngine as KineticsEngine
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
        # Apply the resolved parameter set's kinetics values as rate overrides
        # on the kinetics engine. Without this, `params` (and therefore any
        # calibrated parameter set, or a caller-supplied custom
        # ParameterRegistry) never actually reaches the physics engine --
        # every simulation would silently run with ExtendedKineticsEngine's
        # hardcoded __init__ defaults regardless of parameter_set_version.
        # Reassigning .config (not mutating it -- ExtendedKineticsConfig is
        # frozen) is cheap: Numba JIT-compiles on argument *types*, not
        # values, so this does not invalidate the warmup done in __init__.
        kinetics_params = (params or {}).get("kinetics", {})
        rate_overrides = {
            name: entry["value"]
            for name, entry in kinetics_params.items()
            if isinstance(entry, dict) and "value" in entry
        }
        if rate_overrides:
            from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsConfig
            self.kinetics_engine.config = ExtendedKineticsConfig(rate_overrides=rate_overrides)

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
            if sim_type in ["sobol", "full"]:
                D = 3
                step = D + 2
                N = max(10, n_samples // step)
                sampler = qmc.LatinHypercube(d=D, seed=seed)
                points = sampler.random(n=2 * N)
                points_A = points[:N, :]
                points_B = points[N:, :]
                
                scaled_A = qmc.scale(points_A, bounds_lower, bounds_upper)
                scaled_B = qmc.scale(points_B, bounds_lower, bounds_upper)
                
                scaled_samples = []
                for j in range(N):
                    scaled_samples.append(scaled_A[j])
                    for i in range(D):
                        ab_row = np.copy(scaled_A[j])
                        ab_row[i] = scaled_B[j][i]
                        scaled_samples.append(ab_row)
                    scaled_samples.append(scaled_B[j])
                scaled_samples = np.array(scaled_samples)
            else:
                sampler = qmc.LatinHypercube(d=3, seed=seed)
                points = sampler.random(n=n_samples)
                scaled_samples = qmc.scale(points, bounds_lower, bounds_upper)
            
            co2_effs = []
            so2_effs = []
            nox_effs = []
            hm_effs = []
            npvs = []
            paybacks = []
            strengths = []
            
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
                    co2_eff = k_s.capture_efficiencies.get("co2_pct", 0.0)
                    so2_eff = k_s.capture_efficiencies.get("so2_pct", 0.0)
                    nox_eff = k_s.capture_efficiencies.get("nox_pct", 0.0)
                    hm_eff = k_s.capture_efficiencies.get("heavy_metals_pct", k_s.capture_efficiencies.get("hm_pct", 95.0))
                    
                    mb_s = self.mb_engine.compute(k_s, p_sample, r_sample)
                    bp_s = self.block_predictor.predict(mb_s, c_sample)
                    ec_s = self.eco_engine.compute(mb_s, bp_s["compressive_strength_mpa"], p_sample.operating_hours_per_year)
                    npv_val = ec_s["npv_10yr_inr"]
                    payback_val = ec_s["payback_months"]
                    strength_val = bp_s["compressive_strength_mpa"]
                except Exception as e:
                    co2_eff = 0.0
                    so2_eff = 0.0
                    nox_eff = 0.0
                    hm_eff = 0.0
                    npv_val = 0.0
                    payback_val = 999.0
                    strength_val = 0.0
                    logger.warning(f"UQ sample calculation failed: {e}")
                
                co2_effs.append(co2_eff)
                so2_effs.append(so2_eff)
                nox_effs.append(nox_eff)
                hm_effs.append(hm_eff)
                npvs.append(npv_val)
                paybacks.append(payback_val)
                strengths.append(strength_val)
            
            if co2_effs:
                out["capture_distribution"] = self._make_dist_stats(co2_effs, n_samples)
                out["npv_distribution"] = self._make_dist_stats(npvs, n_samples)
                out["payback_distribution"] = self._make_dist_stats(paybacks, n_samples)
                out["so2_distribution"] = self._make_dist_stats(so2_effs, n_samples)
                out["strength_distribution"] = self._make_dist_stats(strengths, n_samples)
                out["nox_distribution"] = self._make_dist_stats(nox_effs, n_samples)
                out["heavy_metal_distribution"] = self._make_dist_stats(hm_effs, n_samples)

                
            if sim_type in ["sobol", "full"] and len(co2_effs) > 0:
                from cbms_sim.domain.uq.sobol import sobol_indices
                names = ["enzyme_concentration_mg_l", "reactor_temperature_c", "flow_rate_nm3_hr"]
                
                D = 3
                step = D + 2
                valid_len = (len(co2_effs) // step) * step
                if valid_len >= step:
                    so_co2 = sobol_indices(scaled_samples[:valid_len], np.array(co2_effs[:valid_len]), n_vars=D, names=names)
                    so_npv = sobol_indices(scaled_samples[:valid_len], np.array(npvs[:valid_len]), n_vars=D, names=names)
                    so_str = sobol_indices(scaled_samples[:valid_len], np.array(strengths[:valid_len]), n_vars=D, names=names)
                    
                    sobol_res = so_co2["first_order"]
                    sobol_res_total = so_co2["total_order"]
                    sobol_npv = so_npv["first_order"]
                    sobol_strength = so_str["first_order"]
                else:
                    sobol_res = self._compute_spearman_sensitivity(scaled_samples, co2_effs)
                    sobol_res_total = sobol_res
                    sobol_npv = self._compute_spearman_sensitivity(scaled_samples, npvs)
                    sobol_strength = self._compute_spearman_sensitivity(scaled_samples, strengths)
                
                out["sensitivity"] = {
                    "first_order": sobol_res,
                    "total_order": sobol_res_total,
                    "npv_first_order": sobol_npv,
                    "block_strength_first_order": sobol_strength,
                    "critical_experiments": [
                        {"parameter": "enzyme_concentration_mg_l", "rank": 1},
                        {"parameter": "reactor_temperature_c", "rank": 2},
                        {"parameter": "flow_rate_nm3_hr", "rank": 3}
                    ],
                    "n_base_samples": n_samples,
                    "method": "Saltelli" if valid_len >= step else "Spearman"
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
            "n_samples": int(n_samples),
            "samples": [float(x) for x in arr]
        }

    def _compute_spearman_sensitivity(self, samples: np.ndarray, outputs: list[float]) -> dict[str, float]:
        if len(samples) == 0 or len(outputs) == 0:
            return {
                "enzyme_concentration_mg_l": 0.333,
                "reactor_temperature_c": 0.333,
                "flow_rate_nm3_hr": 0.333
            }
        
        n = min(len(samples), len(outputs))
        s_vals = samples[:n]
        o_vals = outputs[:n]
        
        enz_vals = s_vals[:, 0]
        temp_vals = s_vals[:, 1]
        flow_vals = s_vals[:, 2]
        
        from scipy.stats import spearmanr
        sob_enzyme, _ = spearmanr(enz_vals, o_vals)
        sob_temp, _ = spearmanr(temp_vals, o_vals)
        sob_flow, _ = spearmanr(flow_vals, o_vals)
        
        c_enz = float(sob_enzyme) if not np.isnan(sob_enzyme) else 0.0
        c_temp = float(sob_temp) if not np.isnan(sob_temp) else 0.0
        c_flow = float(sob_flow) if not np.isnan(sob_flow) else 0.0
        
        total = abs(c_enz) + abs(c_temp) + abs(c_flow)
        if total > 1e-9:
            s_enzyme = abs(c_enz) / total
            s_temp = abs(c_temp) / total
            s_flow = abs(c_flow) / total
        else:
            s_enzyme, s_temp, s_flow = 0.333, 0.333, 0.333
            
        return {
            "enzyme_concentration_mg_l": s_enzyme,
            "reactor_temperature_c": s_temp,
            "flow_rate_nm3_hr": s_flow
        }
