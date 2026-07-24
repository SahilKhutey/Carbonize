"""
Parametric model fitting using scipy.optimize.

Fits Michaelis-Menten, Freundlich isotherms, and precipitation kinetics
to experimental data using non-linear least squares.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import t as t_dist

from cbms_shared.exceptions import CBMSError
from cbms_shared.logging import get_logger
from cbms_sim.domain.experimental.config import CONFIG
from .models import (
    ca_rate_model as models_ca_rate_model,
    caco3_precipitation_rate as models_caco3_rate,
    multi_gas_removal_efficiency as models_multi_gas_efficiency,
    formulation_strength_response as models_formulation_response,
)

logger = get_logger(__name__)


@dataclass
class FitResult:
    """Result of a parameter fit."""
    parameters: Dict[str, float]
    parameter_stderr: Dict[str, float]
    parameter_ci: Dict[str, Tuple[float, float]]
    covariance: np.ndarray
    r_squared: float
    rmse: float
    mae: float
    aic: float
    bic: float
    residuals: np.ndarray
    n_observations: int
    n_parameters: int
    degrees_of_freedom: int
    fit_quality: str
    model_name: str
    convergence: bool
    notes: List[str] = field(default_factory=list)


class ParameterFitter:
    """Fit parameters to experimental data using parametric models."""
    
    def __init__(self, experiment: str):
        self.experiment = experiment
        self.logger = get_logger(self.__class__.__name__)
    
    def _build_fit_result(
        self,
        y_obs: np.ndarray,
        y_pred: np.ndarray,
        popt: np.ndarray,
        jac: np.ndarray | None,
        param_keys: List[str],
        model_name: str,
        converged: bool,
        bounds: tuple | None = None,
        notes: List[str] | None = None,
    ) -> FitResult:
        """
        Shared helper for computing R², RMSE, MAE, covariance, standard errors,
        confidence intervals, AIC, BIC, and fit quality classification.
        """
        notes_list = list(notes or [])
        if bounds is not None and len(bounds) == 2:
            lower_bounds, upper_bounds = bounds
            for i, key in enumerate(param_keys):
                if i < len(popt) and i < len(lower_bounds) and i < len(upper_bounds):
                    val = float(popt[i])
                    lb = float(lower_bounds[i])
                    ub = float(upper_bounds[i])
                    if abs(val - lb) <= 1e-4 * max(1.0, abs(lb)) or abs(val - ub) <= 1e-4 * max(1.0, abs(ub)):
                        notes_list.append(f"Parameter {key} pinned to bound [{lb}, {ub}]")

        residuals = y_obs - y_pred
        ss_res = float(np.sum(residuals**2))
        ss_tot = float(np.sum((y_obs - np.mean(y_obs))**2))
        r_squared = float(1.0 - ss_res / ss_tot) if ss_tot != 0.0 else 0.0
        rmse = float(np.sqrt(np.mean(residuals**2))) if len(residuals) > 0 else 0.0
        mae = float(np.mean(np.abs(residuals))) if len(residuals) > 0 else 0.0
        n = len(y_obs)
        k = len(popt)
        dof = max(n - k, 1)

        try:
            if jac is not None and jac.size > 0:
                cov = np.linalg.inv(jac.T @ jac) * (ss_res / dof)
                se = np.sqrt(np.diag(cov))
                t_crit = t_dist.ppf(0.975, dof)
                ci_list = [
                    (float(popt[i] - t_crit * se[i]), float(popt[i] + t_crit * se[i]))
                    for i in range(k)
                ]
            else:
                raise ValueError("No jacobian provided")
        except Exception:
            self.logger.warning("covariance_calculation_failed", model_name=model_name)
            cov = np.full((k, k), np.nan)
            se = np.full(k, np.nan)
            ci_list = [(float(np.nan), float(np.nan)) for _ in range(k)]

        aic = float(n * np.log(ss_res / n) + 2 * k) if n > 0 and ss_res > 0 else 0.0
        bic = float(n * np.log(ss_res / n) + k * np.log(n)) if n > 0 and ss_res > 0 else 0.0
        fit_quality = self._classify_fit_quality(r_squared, rmse, mae, float(y_obs.mean()) if len(y_obs) > 0 else 0.0)

        param_dict = {key: float(popt[i]) for i, key in enumerate(param_keys)}
        stderr_dict = {key: float(se[i]) for i, key in enumerate(param_keys)}
        ci_dict = {key: ci_list[i] for i, key in enumerate(param_keys)}

        return FitResult(
            parameters=param_dict,
            parameter_stderr=stderr_dict,
            parameter_ci=ci_dict,
            covariance=cov,
            r_squared=r_squared,
            rmse=rmse,
            mae=mae,
            aic=aic,
            bic=bic,
            residuals=residuals,
            n_observations=n,
            n_parameters=k,
            degrees_of_freedom=dof,
            fit_quality=fit_quality,
            model_name=model_name,
            convergence=converged,
            notes=notes_list,
        )

    def fit(
        self,
        data: pd.DataFrame,
        baseline_params: dict,
    ) -> FitResult:
        """
        Fit parameters for the given experiment.
        """
        if self.experiment == "CE-1":
            return self._fit_ce1_ca_kinetics(data, baseline_params)
        elif self.experiment == "CE-2":
            return self._fit_ce2_metal_sorption(data, baseline_params)
        elif self.experiment == "CE-3":
            return self._fit_ce3_precipitation(data, baseline_params)
        elif self.experiment == "CE-4":
            return self._fit_ce4_multi_gas(data, baseline_params)
        elif self.experiment == "CE-5":
            return self._fit_ce5_formulation(data, baseline_params)
        else:
            raise CBMSError(f"No fitter implemented for {self.experiment}")
            
    def _fit_ce1_ca_kinetics(
        self,
        data: pd.DataFrame,
        baseline: dict,
    ) -> FitResult:
        self.logger.info("fitting_ce1_ca_kinetics", n_points=len(data))
        
        # Safe lookup in baseline parameters
        try:
            k_cat_base = baseline["parameters"]["kinetics.k_cat"]["value"]
            K_M_base = baseline["parameters"]["kinetics.K_M_co2"]["value"]
            K_i_base = baseline["parameters"]["kinetics.K_i_hco3"]["value"]
            # Registry stores this in kJ/mol (e.g. 85.0); fitter optimizer works in J/mol
            E_a_base = baseline["parameters"]["kinetics.E_a_inact"]["value"] * 1000.0
            if E_a_base > 500e3:  # handle legacy unscaled values from prior bug
                E_a_base = 85.0e3
        except KeyError:
            k_cat_base = 1.0e6
            K_M_base = 8.5
            K_i_base = 26.0
            E_a_base = 85.0e3
            
        def ca_rate_model(X, k_cat, K_M, K_i, E_a):
            T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM = X
            return models_ca_rate_model(T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM, k_cat, K_M, K_i, E_a)
        
        T_K = data["temperature_C"].values + 273.15
        pH = data["pH"].values
        CO2 = data["CO2_mM"].values
        CA = data["CA_U_per_mL"].values
        HCO3 = data["HCO3_mM"].fillna(0).values
        rate_obs = data["rate_mol_per_L_s"].values
        
        X = np.array([T_K, pH, CO2, CA, HCO3])
        y = rate_obs
        
        p0 = [k_cat_base, K_M_base, K_i_base, E_a_base]
        bounds = (
            [1e3, 0.1, 1.0, 10e3],
            [1e9, 100.0, 500.0, 200e3],
        )
        
        try:
            result = least_squares(
                self._residuals_ca,
                p0,
                args=(X, y),
                bounds=bounds,
                method='trf',
                max_nfev=10000,
            )
            popt = result.x
            converged = result.success
        except Exception as e:
            self.logger.error("fit_failed_ca", error=str(e))
            raise
            
        y_pred = ca_rate_model(X, *popt)

        # Convert E_a from J/mol back to kJ/mol for registry and output parameter set
        popt_export = popt.copy()
        popt_export[3] = popt[3] / 1000.0

        jac_export = result.jac.copy()
        jac_export[:, 3] = result.jac[:, 3] * 1000.0  # d(rate)/d(E_a_kJ) = d(rate)/d(E_a_J) * 1000

        return self._build_fit_result(
            y_obs=y,
            y_pred=y_pred,
            popt=popt_export,
            jac=jac_export,
            param_keys=[
                "kinetics.k_cat",
                "kinetics.K_M_co2",
                "kinetics.K_i_hco3",
                "kinetics.E_a_inact",
            ],
            model_name="CE-1",
            converged=converged,
            bounds=bounds,
        )

    def _residuals_ca(self, params, X, y_obs):
        T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM = X
        k_cat, K_M, K_i, E_a = params
        y_pred = models_ca_rate_model(T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM, k_cat, K_M, K_i, E_a)
        return y_obs - y_pred

    def _fit_ce2_metal_sorption(
        self,
        data: pd.DataFrame,
        baseline: dict,
    ) -> FitResult:
        self.logger.info("fitting_ce2_metal_sorption", n_points=len(data))
        all_results = {}
        combined_residuals = []
        combined_y = []
        
        for metal in ["Pb", "Cd", "Hg", "As"]:
            metal_data = data[data["metal"] == metal]
            if len(metal_data) < 3:
                continue
            Ce = metal_data["equilibrium_conc_mg_L"].values
            qe = metal_data["loading_mg_per_g"].values
            mask = (Ce > 0) & (qe > 0)
            Ce, qe = Ce[mask], qe[mask]
            
            if len(Ce) < 2:
                continue
                
            ln_Ce = np.log(Ce)
            ln_qe = np.log(qe)
            coeffs = np.polyfit(ln_Ce, ln_qe, 1)
            one_over_n = coeffs[0]
            K_F = np.exp(coeffs[1])
            n = 1.0 / one_over_n
            
            all_results[f"kinetics.K_F_{metal}"] = float(K_F)
            all_results[f"kinetics.n_{metal}"] = float(n)
            
            residuals_metal = qe - K_F * Ce**(1.0 / n)
            combined_residuals.extend(residuals_metal.tolist())
            combined_y.extend(qe.tolist())
            
        combined_residuals = np.array(combined_residuals)
        combined_y = np.array(combined_y)
        ss_res = np.sum(combined_residuals**2)
        ss_tot = np.sum((combined_y - combined_y.mean())**2) if len(combined_y) > 0 else 1.0
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
        rmse = np.sqrt(np.mean(combined_residuals**2)) if len(combined_residuals) > 0 else 0.0
        mae = np.mean(np.abs(combined_residuals)) if len(combined_residuals) > 0 else 0.0
        
        return FitResult(
            parameters=all_results,
            parameter_stderr={},
            parameter_ci={},
            covariance=np.array([]),
            r_squared=float(r_squared),
            rmse=float(rmse),
            mae=float(mae),
            aic=0.0,
            bic=0.0,
            residuals=combined_residuals,
            n_observations=len(combined_y),
            n_parameters=len(all_results),
            degrees_of_freedom=len(combined_y) - len(all_results),
            fit_quality="GOOD",
            model_name="CE-2",
            convergence=True,
        )

    def _fit_ce3_precipitation(
        self,
        data: pd.DataFrame,
        baseline: dict,
    ) -> FitResult:
        self.logger.info("fitting_ce3_precipitation", n_points=len(data))

        try:
            k_precip_base = baseline["parameters"]["kinetics.k_precip_caco3"]["value"]
        except KeyError:
            k_precip_base = 1.5e-2

        Ca_mM = data["Ca_mM"].values
        HCO3_mM = data["HCO3_mM"].values
        chitosan_pct = data["chitosan_pct"].values if "chitosan_pct" in data.columns else np.ones(len(data))
        pH = data["pH"].values if "pH" in data.columns else np.full(len(data), 8.5)
        rate_obs = data["rate_mol_per_L_s"].values

        p0 = [k_precip_base]
        bounds = ([1e-6], [10.0])

        def residuals_ce3(params, Ca, HCO3, chitosan, pH_val, y_obs):
            k_precip = params[0]
            y_pred = models_caco3_rate(Ca, HCO3, k_precip, chitosan, pH_val)
            return y_obs - y_pred

        try:
            result = least_squares(
                residuals_ce3,
                p0,
                args=(Ca_mM, HCO3_mM, chitosan_pct, pH, rate_obs),
                bounds=bounds,
                method="trf",
                max_nfev=10000,
            )
            popt = result.x
            converged = result.success
        except Exception as e:
            self.logger.error("fit_failed_ce3", error=str(e))
            raise

        y_pred = models_caco3_rate(Ca_mM, HCO3_mM, popt[0], chitosan_pct, pH)

        return self._build_fit_result(
            y_obs=rate_obs,
            y_pred=y_pred,
            popt=popt,
            jac=result.jac,
            param_keys=["kinetics.k_precip_caco3"],
            model_name="CE-3",
            converged=converged,
            notes=[],
        )

    def _fit_ce4_multi_gas(
        self,
        data: pd.DataFrame,
        baseline: dict,
    ) -> FitResult:
        self.logger.info("fitting_ce4_multi_gas", n_points=len(data))

        # Single source of truth for reactor geometry residence time
        base_tau = float(CONFIG.geometry.RESIDENCE_TIME)

        try:
            k_so2_base = baseline["parameters"]["kinetics.k_so2_abs"]["value"]
        except KeyError:
            k_so2_base = 2.5e-2

        try:
            k_no2_base = baseline["parameters"]["kinetics.k_no2_abs"]["value"]
        except KeyError:
            k_no2_base = 1.0e-2

        inlet = data["inlet_ppm"].values
        outlet = data["outlet_ppm"].values
        # Target column matches comparator resolution: removal efficiency (%)
        y_obs = np.where(inlet > 0, ((inlet - outlet) / inlet) * 100.0, 0.0)

        # Derive residence time per row based on L_per_min flow rate vs nominal 10.0 L/min bench flow
        flow_l_pm = data["L_per_min"].values if "L_per_min" in data.columns else np.full(len(data), 10.0)
        t_res = np.where(flow_l_pm > 0, base_tau * (10.0 / flow_l_pm), base_tau)

        gas_series = data["gas"].astype(str)
        so2_mask = (gas_series == "SO2").values
        nox_mask = (gas_series.isin(["NOx", "NO2"])).values

        def residuals_gas(params, t_res_sub, y_obs_sub):
            k_abs = params[0]
            y_pred_sub = models_multi_gas_efficiency(k_abs, t_res_sub)
            return y_obs_sub - y_pred_sub

        bounds = ([1e-5], [10.0])

        # 1. Fit SO2 absorption rate constant
        popt_so2 = np.array([k_so2_base])
        converged_so2 = True
        if np.any(so2_mask):
            try:
                res_so2 = least_squares(
                    residuals_gas,
                    [k_so2_base],
                    args=(t_res[so2_mask], y_obs[so2_mask]),
                    bounds=bounds,
                    method="trf",
                    max_nfev=10000,
                )
                popt_so2 = res_so2.x
                converged_so2 = res_so2.success
            except Exception as e:
                self.logger.error("fit_failed_ce4_so2", error=str(e))
                raise

        # 2. Fit NOx/NO2 absorption rate constant
        popt_no2 = np.array([k_no2_base])
        converged_no2 = True
        if np.any(nox_mask):
            try:
                res_no2 = least_squares(
                    residuals_gas,
                    [k_no2_base],
                    args=(t_res[nox_mask], y_obs[nox_mask]),
                    bounds=bounds,
                    method="trf",
                    max_nfev=10000,
                )
                popt_no2 = res_no2.x
                converged_no2 = res_no2.success
            except Exception as e:
                self.logger.error("fit_failed_ce4_no2", error=str(e))
                raise

        # 3. Combine predictions and construct block diagonal Jacobian matrix
        y_pred = np.zeros(len(data))
        if np.any(so2_mask):
            y_pred[so2_mask] = models_multi_gas_efficiency(popt_so2[0], t_res[so2_mask])
        if np.any(nox_mask):
            y_pred[nox_mask] = models_multi_gas_efficiency(popt_no2[0], t_res[nox_mask])

        # Block-diagonal Jacobian of shape (n_obs, 2)
        jac_combined = np.zeros((len(data), 2))
        if np.any(so2_mask):
            jac_combined[so2_mask, 0] = t_res[so2_mask] * np.exp(-popt_so2[0] * t_res[so2_mask]) * 100.0
        if np.any(nox_mask):
            jac_combined[nox_mask, 1] = t_res[nox_mask] * np.exp(-popt_no2[0] * t_res[nox_mask]) * 100.0

        popt_combined = np.array([popt_so2[0], popt_no2[0]])
        param_keys = ["kinetics.k_so2_abs", "kinetics.k_no2_abs"]

        notes = []
        if "pH" in data.columns and data["pH"].nunique() > 1:
            notes.append("pH varies across multi-gas bench runs (unmodeled sulfite/bisulfite equilibrium shift)")

        return self._build_fit_result(
            y_obs=y_obs,
            y_pred=y_pred,
            popt=popt_combined,
            jac=jac_combined,
            param_keys=param_keys,
            model_name="CE-4",
            converged=converged_so2 and converged_no2,
            notes=notes,
        )

    def _fit_ce5_formulation(
        self,
        data: pd.DataFrame,
        baseline: dict,
    ) -> FitResult:
        self.logger.info("fitting_ce5_formulation", n_points=len(data))

        try:
            coeff_base = baseline["parameters"]["kinetics.strength_coeff_chitosan"]["value"]
        except KeyError:
            coeff_base = 2.5

        try:
            ph_mod_base = baseline["parameters"]["kinetics.pH_coeff_strength"]["value"]
        except KeyError:
            ph_mod_base = 0.1

        chitosan_pct = data["chitosan_pct"].values
        pH = data["pH"].values
        y_obs = data["response"].values

        p0 = [coeff_base, ph_mod_base]
        bounds = ([0.01, 0.0], [50.0, 5.0])

        def residuals_ce5(params, chitosan, pH_val, y_actual):
            coeff, ph_mod = params
            y_pred = models_formulation_response(chitosan, pH_val, coeff, ph_mod)
            return y_actual - y_pred

        try:
            result = least_squares(
                residuals_ce5,
                p0,
                args=(chitosan_pct, pH, y_obs),
                bounds=bounds,
                method="trf",
                max_nfev=10000,
            )
            popt = result.x
            converged = result.success
        except Exception as e:
            self.logger.error("fit_failed_ce5", error=str(e))
            raise

        y_pred = models_formulation_response(chitosan_pct, pH, popt[0], popt[1])
        notes = ["Calibrated compressive strength response against bench chitosan/pH screen"]

        return self._build_fit_result(
            y_obs=y_obs,
            y_pred=y_pred,
            popt=popt,
            jac=result.jac,
            param_keys=["kinetics.strength_coeff_chitosan", "kinetics.pH_coeff_strength"],
            model_name="CE-5",
            converged=converged,
            notes=notes,
        )

    def _classify_fit_quality(self, r2: float, rmse: float, mae: float, y_mean: float) -> str:
        cv_rmse = rmse / abs(y_mean) if y_mean != 0 else float('inf')
        if r2 >= 0.95 and cv_rmse < 0.10:
            return "GOOD"
        elif r2 >= 0.90 and cv_rmse < 0.20:
            return "ACCEPTABLE"
        else:
            return "POOR"
