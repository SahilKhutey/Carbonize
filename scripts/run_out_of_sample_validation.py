"""
scripts/run_out_of_sample_validation.py
Out-of-sample predictive validation runner for held-out pilot plant reactor observations.

Performs pure forward predictions using calibrated v2026.2 parameters directly against
held-out pilot observations (without re-fitting parameters) to verify true model generalization.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure shared and sim-core are on sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "packages" / "shared" / "src"))
sys.path.insert(0, str(root_dir / "packages" / "sim-core" / "src"))

from calibration.models import (
    ca_rate_model,
    freundlich_isotherm,
    multi_gas_removal_efficiency,
    formulation_strength_response,
)
from calibration.fitters import FitResult
from calibration.comparator import PredictionComparator
from cbms_sim.domain.parameters import ParameterRegistry


def _extract_param(registry: ParameterRegistry, key: str, default: float) -> float:
    """Safely extract a float parameter value from registry."""
    val = registry.get(key)
    if val is None:
        return default
    if isinstance(val, dict):
        return float(val.get("value", default))
    return float(val)


def run_held_out_validation():
    pilot_csv = root_dir / "data/pilot_data/held_out_pilot_observations.csv"
    if not pilot_csv.exists():
        print(f"Error: {pilot_csv} does not exist.")
        sys.exit(1)

    df_pilot = pd.read_csv(pilot_csv)
    comparator = PredictionComparator()
    param_file = root_dir / "data/parameters/v2026.2.json"
    registry = ParameterRegistry.from_file(param_file)

    results = []

    # -------------------------------------------------------------------------
    # 1. CE-1 Out-of-sample Forward Evaluation (CA Kinetics)
    # -------------------------------------------------------------------------
    df_ce1 = df_pilot[df_pilot["experiment"] == "CE-1"].copy()
    if len(df_ce1) > 0:
        for col in ["temperature_C", "pH", "CO2_mM", "CA_U_per_mL", "HCO3_mM", "rate_mol_per_L_s"]:
            df_ce1[col] = pd.to_numeric(df_ce1[col], errors="coerce")

        k_cat = _extract_param(registry, "kinetics.k_cat", 2.45e6)
        km_co2 = _extract_param(registry, "kinetics.K_M_co2", 20.9)
        ki_hco3 = _extract_param(registry, "kinetics.K_i_hco3", 15.28)
        ea_inact = _extract_param(registry, "kinetics.E_a_inact", 13.4)

        y_obs = df_ce1["rate_mol_per_L_s"].values
        temp_c = df_ce1["temperature_C"].fillna(25.0).values
        t_k = temp_c + 273.15
        co2_val = df_ce1["CO2_mM"].values
        ph_val = df_ce1["pH"].values
        ca_val = df_ce1["CA_U_per_mL"].values
        hco3_val = df_ce1["HCO3_mM"].values

        y_pred = ca_rate_model(t_k, ph_val, co2_val, ca_val, hco3_val, k_cat, km_co2, ki_hco3, ea_inact)
        residuals = y_obs - y_pred

        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 1.0
        rmse = float(np.sqrt(np.mean(residuals**2)))
        mae = float(np.mean(np.abs(residuals)))

        fit_ce1 = FitResult(
            parameters={"k_cat": k_cat, "K_M_co2": km_co2, "K_i_hco3": ki_hco3, "E_a_inact": ea_inact},
            parameter_stderr={},
            parameter_ci={},
            covariance=np.zeros((4, 4)),
            r_squared=round(r2, 4),
            rmse=rmse,
            mae=mae,
            aic=0.0,
            bic=0.0,
            residuals=residuals,
            n_observations=len(y_obs),
            n_parameters=0,
            degrees_of_freedom=len(y_obs),
            fit_quality="ACCEPTABLE" if r2 >= 0.8 else "POOR",
            model_name="CE-1",
            convergence=True,
            notes=["Held-out pilot forward prediction using fixed v2026.2 parameters"],
        )
        comp_ce1 = comparator.compare(fit_ce1, df_ce1, "CE-1", evaluation_mode="HELD_OUT_PILOT")
        results.append(comp_ce1)

    # -------------------------------------------------------------------------
    # 2. CE-2 Out-of-sample Forward Evaluation (Heavy Metal Sorption)
    # -------------------------------------------------------------------------
    df_ce2 = df_pilot[df_pilot["experiment"] == "CE-2"].copy()
    if len(df_ce2) > 0:
        for col in ["equilibrium_conc_mg_L", "loading_mg_per_g"]:
            df_ce2[col] = pd.to_numeric(df_ce2[col], errors="coerce")

        kf_pb = _extract_param(registry, "kinetics.K_F_Pb", 13.197)
        n_pb = _extract_param(registry, "kinetics.n_Pb", 2.169)
        kf_cd = _extract_param(registry, "kinetics.K_F_Cd", 5.51)
        n_cd = _extract_param(registry, "kinetics.n_Cd", 1.729)
        kf_hg = _extract_param(registry, "kinetics.K_F_Hg", 24.01)
        n_hg = _extract_param(registry, "kinetics.n_Hg", 2.42)

        y_obs = df_ce2["loading_mg_per_g"].values
        metals = df_ce2["metal"].astype(str).values
        c_eqs = df_ce2["equilibrium_conc_mg_L"].values

        y_pred = np.zeros(len(df_ce2))
        for i in range(len(df_ce2)):
            m = metals[i]
            c = c_eqs[i]
            if m == "Pb":
                y_pred[i] = freundlich_isotherm(c, kf_pb, n_pb)
            elif m == "Cd":
                y_pred[i] = freundlich_isotherm(c, kf_cd, n_cd)
            elif m == "Hg":
                y_pred[i] = freundlich_isotherm(c, kf_hg, n_hg)
            else:
                y_pred[i] = freundlich_isotherm(c, kf_pb, n_pb)

        residuals = y_obs - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 1.0
        rmse = float(np.sqrt(np.mean(residuals**2)))
        mae = float(np.mean(np.abs(residuals)))

        fit_ce2 = FitResult(
            parameters={
                "K_F_Pb": kf_pb, "n_Pb": n_pb,
                "K_F_Cd": kf_cd, "n_Cd": n_cd,
                "K_F_Hg": kf_hg, "n_Hg": n_hg,
            },
            parameter_stderr={},
            parameter_ci={},
            covariance=np.zeros((6, 6)),
            r_squared=round(r2, 4),
            rmse=rmse,
            mae=mae,
            aic=0.0,
            bic=0.0,
            residuals=residuals,
            n_observations=len(y_obs),
            n_parameters=0,
            degrees_of_freedom=len(y_obs),
            fit_quality="ACCEPTABLE" if r2 >= 0.8 else "POOR",
            model_name="CE-2",
            convergence=True,
            notes=["Held-out pilot forward prediction using fixed v2026.2 parameters"],
        )
        comp_ce2 = comparator.compare(fit_ce2, df_ce2, "CE-2", evaluation_mode="HELD_OUT_PILOT")
        results.append(comp_ce2)

    # -------------------------------------------------------------------------
    # 3. CE-4 Out-of-sample Forward Evaluation (Multi-Gas Absorption)
    # -------------------------------------------------------------------------
    df_ce4 = df_pilot[df_pilot["experiment"] == "CE-4"].copy()
    if len(df_ce4) > 0:
        for col in ["inlet_ppm", "outlet_ppm", "L_per_min"]:
            df_ce4[col] = pd.to_numeric(df_ce4[col], errors="coerce")

        k_so2 = _extract_param(registry, "kinetics.k_so2_abs", 0.1147)
        k_no2 = _extract_param(registry, "kinetics.k_no2_abs", 0.0492)

        # CE-4 target evaluated by comparator is removal efficiency (%)
        inlet_vals = df_ce4["inlet_ppm"].values
        outlet_vals = df_ce4["outlet_ppm"].values
        gases = df_ce4["gas"].astype(str).values
        flow_vals = df_ce4["L_per_min"].values

        y_obs = ((inlet_vals - outlet_vals) / np.maximum(inlet_vals, 1e-6)) * 100.0
        y_pred = np.zeros(len(df_ce4))
        for i in range(len(df_ce4)):
            t_res = (1.0 / max(flow_vals[i], 0.1)) * 60.0
            k_abs = k_so2 if gases[i] == "SO2" else k_no2
            y_pred[i] = multi_gas_removal_efficiency(k_abs, t_res)

        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
        if np.isnan(r2):
            r2 = 0.0
        rmse = float(np.sqrt(np.mean(residuals**2)))
        mae = float(np.mean(np.abs(residuals)))

        fit_ce4 = FitResult(
            parameters={"k_so2_abs": k_so2, "k_no2_abs": k_no2},
            parameter_stderr={},
            parameter_ci={},
            covariance=np.zeros((2, 2)),
            r_squared=round(r2, 4),
            rmse=rmse,
            mae=mae,
            aic=0.0,
            bic=0.0,
            residuals=residuals,
            n_observations=len(y_obs),
            n_parameters=0,
            degrees_of_freedom=len(y_obs),
            fit_quality="ACCEPTABLE" if r2 >= 0.8 else "POOR",
            model_name="CE-4",
            convergence=True,
            notes=["Held-out pilot forward prediction using fixed v2026.2 parameters"],
        )
        comp_ce4 = comparator.compare(fit_ce4, df_ce4, "CE-4", evaluation_mode="HELD_OUT_PILOT")
        results.append(comp_ce4)

    # -------------------------------------------------------------------------
    # 4. CE-5 Out-of-sample Forward Evaluation (Formulation Screen)
    # -------------------------------------------------------------------------
    df_ce5 = df_pilot[df_pilot["experiment"] == "CE-5"].copy()
    if len(df_ce5) > 0:
        for col in ["chitosan_pct", "pH", "response"]:
            df_ce5[col] = pd.to_numeric(df_ce5[col], errors="coerce")
        df_ce5["pH"] = df_ce5["pH"].fillna(8.5)
        df_ce5["chitosan_pct"] = df_ce5["chitosan_pct"].fillna(1.0)

        str_coeff = _extract_param(registry, "kinetics.strength_coeff_chitosan", 2.178)
        ph_mod = _extract_param(registry, "kinetics.pH_coeff_strength", 0.0)

        y_obs = df_ce5["response"].values
        chitosan_pct = df_ce5["chitosan_pct"].values
        ph_val = df_ce5["pH"].values

        y_pred = formulation_strength_response(chitosan_pct, ph_val, str_coeff, ph_mod)
        residuals = y_obs - y_pred

        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 1.0
        rmse = float(np.sqrt(np.mean(residuals**2)))
        mae = float(np.mean(np.abs(residuals)))

        fit_ce5 = FitResult(
            parameters={"strength_coeff_chitosan": str_coeff, "pH_coeff_strength": ph_mod},
            parameter_stderr={},
            parameter_ci={},
            covariance=np.zeros((2, 2)),
            r_squared=round(r2, 4),
            rmse=rmse,
            mae=mae,
            aic=0.0,
            bic=0.0,
            residuals=residuals,
            n_observations=len(y_obs),
            n_parameters=0,
            degrees_of_freedom=len(y_obs),
            fit_quality="ACCEPTABLE" if r2 >= 0.8 else "POOR",
            model_name="CE-5",
            convergence=True,
            notes=["Held-out pilot forward prediction using fixed v2026.2 parameters"],
        )
        comp_ce5 = comparator.compare(fit_ce5, df_ce5, "CE-5", evaluation_mode="HELD_OUT_PILOT")
        results.append(comp_ce5)

    # -------------------------------------------------------------------------
    # Write Executive Out-of-Sample Summary Report
    # -------------------------------------------------------------------------
    summary_path = root_dir / "data/parameters/pilot_validation_summary.md"
    lines = [
        "# 🏭 Real Hardware Pilot Out-of-Sample Validation Summary",
        "",
        "**Evaluation Mode:** `HELD_OUT_PILOT` (Pure Forward Prediction without Re-fitting)",
        "**Parameter Set:** `v2026.2`",
        "",
        "| Experiment | Physical Target | Evaluation Mode | R² Score | RMSE | MAPE % | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for res in results:
        exp = res["experiment"]
        status = res["status"]
        r2 = res.get("r_squared") or 0.0
        rmse = res.get("rmse") or 0.0
        mape = res.get("mape_pct") or 0.0
        badge = "🟢 PILOT_VALIDATED" if status in ("PILOT_VALIDATED", "VALIDATED") else "🔴 UNVALIDATED"
        lines.append(
            f"| **{exp}** | {exp} Pilot Runs | `HELD_OUT_PILOT` | {r2:.4f} | {rmse:.4e} | {mape:.2f}% | {badge} |"
        )

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Pure forward out-of-sample validation completed. Summary saved to {summary_path}")
    return results


if __name__ == "__main__":
    run_held_out_validation()
