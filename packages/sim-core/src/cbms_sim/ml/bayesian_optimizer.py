"""
ml/bayesian_optimizer.py
Implements multi-objective Bayesian optimization using Optuna.
Finds the trade-off curve between block strength and reagent OPEX.
"""

import optuna
from cbms_sim.domain.kinetics.engine import KineticsEngine
from cbms_sim.domain.mass_balance.engine import MassBalanceEngine
from cbms_sim.domain.block.strength import BlockStrengthPredictor
from cbms_sim.domain.economic.engine import EconomicEngine

from cbms_sim.domain.models.plant import PlantProfile as DomainPlant
from cbms_sim.domain.models.reagent import ReagentFormulation as DomainReagent, CalciumSourceType as DomainCalciumSource
from cbms_sim.domain.models.conditions import OperatingConditions as DomainConditions

def objective(trial):
    """
    Optuna objective function targeting block strength and system payback period.
    """
    # 1. Sample inputs within operational bounds
    enzyme = trial.suggest_float("enzyme_concentration_mg_l", 1.0, 50.0)
    chitosan = trial.suggest_float("chitosan_wt_pct", 1.0, 5.0)
    press_force = trial.suggest_int("press_force_bar", 50, 500)

    # 2. Build domain input records
    plant = DomainPlant(
        exhaust_flow_nm3_hr=10000.0,
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        fly_ash_g_per_nm3=4.5,
    )
    reagent = DomainReagent(
        enzyme_mg_per_l=enzyme,
        chitosan_wt_pct=chitosan,
        ca_source_type=DomainCalciumSource.LIME,
    )
    conditions = DomainConditions(
        press_force_bar=press_force,
        curing_time_h=48.0,
        reactor_temp_c=40.0,
    )

    # 3. Solve pipelines
    k_res = KineticsEngine().solve(plant, reagent, conditions)
    mb_res = MassBalanceEngine().compute(k_res, plant, reagent)
    bp_res = BlockStrengthPredictor().predict(mb_res, conditions)
    eco_res = EconomicEngine().compute(mb_res, bp_res["compressive_strength_mpa"], plant.operating_hours_per_year)

    # We want to maximize strength and minimize annual OPEX
    return bp_res["compressive_strength_mpa"], eco_res["annual_opex_inr"]

def run_parameter_optimization(trials_count: int = 20):
    """
    Executes a study to locate the Pareto frontier.
    """
    # Optimize: Maximize strength, Minimize annual OPEX
    study = optuna.create_study(directions=["maximize", "minimize"])
    study.optimize(objective, n_trials=trials_count)
    return study
