"""
core/uncertainty_engine.py
Implements Latin Hypercube Sampling (LHS) and Sobol/Spearman sensitivity analysis
to calculate output uncertainty distributions for the biomineralization system.
"""

from typing import Dict, Any, TypedDict
import numpy as np
from scipy.stats import qmc
from cbms_sim.core.kinetics import solve_reactor_kinetics

class UQSubmetrics(TypedDict):
    mean: float
    std: float
    p05: float
    p95: float

class UQSO2Submetrics(TypedDict):
    mean: float
    std: float

class UQSensitivity(TypedDict):
    enzyme_concentration_mg_l: float
    reactor_temperature_c: float
    flow_rate_nm3_hr: float

class UQAnalysisResult(TypedDict):
    co2: UQSubmetrics
    so2: UQSO2Submetrics
    sensitivity: UQSensitivity

def run_uncertainty_analysis(
    co2_vol_pct: float,
    so2_mg_per_nm3: float,
    flow_nm3_per_hr: float,
    enzyme_mg_per_l: float,
    reactor_temp_c: float,
    sample_count: int = 30
) -> UQAnalysisResult:
    """Executes Latin Hypercube Sampling (LHS) and sensitivity analysis over kinetics parameters.

    Args:
        co2_vol_pct: Carbon dioxide concentration in flue gas (vol%).
        so2_mg_per_nm3: Sulfur dioxide mass concentration (mg/Nm³).
        flow_nm3_per_hr: Volumetric flue gas flow rate (Nm³/hr).
        enzyme_mg_per_l: Carbonic anhydrase concentration (mg/L).
        reactor_temp_c: Reactor temperature setting (°C).
        sample_count: Number of LHS samples to evaluate. Defaults to 30.

    Returns:
        A UQAnalysisResult dictionary containing statistical aggregations
        and normalized Spearman sensitivity indices.
    """
    # 1. Define input parameters range (mean +/- 20%)
    bounds_lower = np.array([
        max(1.0, enzyme_mg_per_l * 0.8),
        max(20.0, reactor_temp_c * 0.8),
        max(1000.0, flow_nm3_per_hr * 0.8)
    ])
    bounds_upper = np.array([
        min(50.0, enzyme_mg_per_l * 1.2),
        min(65.0, reactor_temp_c * 1.2),
        min(20000.0, flow_nm3_per_hr * 1.2)
    ])

    # 2. Latin Hypercube Sampling (LHS)
    sampler = qmc.LatinHypercube(d=3, seed=42)
    sample_points = sampler.random(n=sample_count)
    scaled_samples = qmc.scale(sample_points, bounds_lower, bounds_upper)

    co2_effs = []
    so2_effs = []

    # 3. Forward solve loop (deterministic ODE runs)
    for sample in scaled_samples:
        enz_val, temp_val, flow_val = sample
        res = solve_reactor_kinetics(
            co2_vol_pct=co2_vol_pct,
            so2_mg_per_nm3=so2_mg_per_nm3,
            flow_nm3_per_hr=flow_val,
            enzyme_mg_per_l=enz_val,
            calcium_source_g_per_l=35.0,
            reactor_temp_c=temp_val
        )
        co2_effs.append(res["co2_capture_efficiency_pct"])
        so2_effs.append(res["so2_capture_efficiency_pct"])

    co2_effs_arr = np.array(co2_effs)
    so2_effs_arr = np.array(so2_effs)

    # 4. Statistical aggregation
    mean_co2 = float(np.mean(co2_effs_arr))
    std_co2 = float(np.std(co2_effs_arr))
    p05_co2 = float(np.percentile(co2_effs_arr, 5))
    p95_co2 = float(np.percentile(co2_effs_arr, 95))

    # 5. Sensitivity Index Calculation (Spearman Rank Correlation)
    from scipy.stats import spearmanr
    
    sob_enzyme, _ = spearmanr(scaled_samples[:, 0], co2_effs_arr)
    sob_temp, _ = spearmanr(scaled_samples[:, 1], co2_effs_arr)
    sob_flow, _ = spearmanr(scaled_samples[:, 2], co2_effs_arr)

    c_enz = float(sob_enzyme) if not np.isnan(sob_enzyme) else 0.0
    c_temp = float(sob_temp) if not np.isnan(sob_temp) else 0.0
    c_flow = float(sob_flow) if not np.isnan(sob_flow) else 0.0

    total_corr = abs(c_enz) + abs(c_temp) + abs(c_flow)
    if total_corr > 1e-9:
        s_enzyme = abs(c_enz) / total_corr
        s_temp = abs(c_temp) / total_corr
        s_flow = abs(c_flow) / total_corr
    else:
        s_enzyme, s_temp, s_flow = 0.3333333333333333, 0.3333333333333333, 0.3333333333333333

    return {
        "co2": {
            "mean": mean_co2,
            "std": std_co2,
            "p05": p05_co2,
            "p95": p95_co2,
        },
        "so2": {
            "mean": float(np.mean(so2_effs_arr)),
            "std": float(np.std(so2_effs_arr)),
        },
        "sensitivity": {
            "enzyme_concentration_mg_l": s_enzyme,
            "reactor_temperature_c": s_temp,
            "flow_rate_nm3_hr": s_flow
        }
    }
