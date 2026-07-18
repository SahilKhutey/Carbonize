"""
ml/bayesian_optimizer.py
Implements multi-objective Bayesian optimization using Optuna.
Finds the trade-off curve between block strength and reagent OPEX.
"""

import optuna
from cbms_sim.core.mass_balance import compute_mass_balance
from cbms_sim.core.block_strength import predict_compressive_strength
from cbms_sim.core.economic_engine import run_financial_analysis

def objective(trial):
    """
    Optuna objective function targeting block strength and system payback period.
    """
    # 1. Sample inputs within operational bounds
    enzyme = trial.suggest_float("enzyme_concentration_mg_l", 1.0, 50.0)
    chitosan = trial.suggest_float("chitosan_wt_pct", 1.0, 5.0)
    press_force = trial.suggest_int("press_force_bar", 50, 500)

    # 2. Run mass balance
    mass_res = compute_mass_balance(
        flow_nm3_per_hr=10000.0,
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        fly_ash_g_per_nm3=4.5,
        chitosan_wt_pct=chitosan,
        enzyme_mg_per_l=enzyme
    )

    # 3. Predict block compressive strength
    strength = predict_compressive_strength(
        mass_balance=mass_res,
        press_force_bar=press_force,
        curing_hours=48.0,
        temperature_c=40.0
    )

    # 4. Predict financials
    financial = run_financial_analysis(
        mass_balance=mass_res,
        flow_nm3_per_hr=10000.0
    )

    # We want to maximize strength and minimize payback horizon (or OPEX)
    # Optuna supports multi-objective optimization out of the box
    return strength, financial.annual_opex_inr

def run_parameter_optimization(trials_count: int = 20):
    """
    Executes a study to locate the Pareto frontier.
    """
    # Optimize: Maximize strength, Minimize annual OPEX
    study = optuna.create_study(directions=["maximize", "minimize"])
    study.optimize(objective, n_trials=trials_count)
    return study
