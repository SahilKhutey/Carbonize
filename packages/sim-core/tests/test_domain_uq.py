"""
tests/test_domain_uq.py
Unit tests verifying the cbms_sim domain UQ, block, and economics integrations.
"""

from decimal import Decimal
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.kinetics import solve_kinetics
from cbms_sim.domain.mass_balance.engine import MassBalanceEngine
from cbms_sim.domain.uq.monte_carlo import MonteCarloEngine
from cbms_sim.domain.uq.sobol import SobolAnalyzer
from cbms_sim.domain.uq.fpt import FirstPassageTime
from cbms_sim.domain.block.strength import BlockStrengthPredictor
from cbms_sim.domain.economic.engine import EconomicEngine

def test_new_domain_pipelines():
    """Verify that UQ, block, and economic model integrations execute correctly."""
    plant = PlantProfile(
        name="LHB Station",
        co2_vol_pct=Decimal("14.0"),
        so2_mg_per_nm3=Decimal("1200.0")
    )
    
    reagent = ReagentFormulation(
        chitosan_wt_pct=Decimal("3.0"),
        enzyme_mg_per_l=Decimal("12.0")
    )
    
    conditions = OperatingConditions(
        reactor_temp_c=Decimal("40.0")
    )
    
    # 1. Run Monte Carlo (LHS)
    mc_engine = MonteCarloEngine(n_samples=5, seed=42)
    uq_res = mc_engine.run(plant, reagent, conditions)
    assert uq_res.statistics["co2"]["mean"] >= 0.0
    
    # 2. Run Sobol Sensitivity
    sobol_analyzer = SobolAnalyzer()
    sens_res = sobol_analyzer.analyze(uq_res)
    assert "enzyme_concentration_mg_l" in sens_res
    
    # 3. FPT
    fpt_calculator = FirstPassageTime()
    fpt_res = fpt_calculator.analytical_fpt(threshold=100.0, drift=5.0, diffusion=1.2)
    assert fpt_res["mean_fpt_hours"] == 20.0
    
    # 4. Block Strength
    kin_res = solve_kinetics(plant, reagent, conditions)
    mb_engine = MassBalanceEngine()
    mb_res = mb_engine.compute(kin_res, plant, reagent)
    
    block_predictor = BlockStrengthPredictor()
    block_res = block_predictor.predict(mb_res, conditions)
    assert block_res["compressive_strength_mpa"] >= 0.0
    
    # 5. Economics
    econ_engine = EconomicEngine()
    econ_res = econ_engine.compute(mb_res, block_res["compressive_strength_mpa"])
    assert econ_res["capex_inr"] > 0.0
