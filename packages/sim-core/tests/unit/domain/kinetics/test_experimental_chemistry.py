import pytest
import numpy as np
from cbms_sim.domain.experimental.experimental_chemistry import ExperimentalBiomineralizationSolver


def test_experimental_solver_run_success():
    """Verify that experimental solver runs successfully and produces correct fields."""
    solver = ExperimentalBiomineralizationSolver(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        nox_inlet_ppm=250.0,
        ca_concentration_mg_l=12.0,
        calcium_source_g_per_l=35.0,
        crosslinking_density=0.0,
        mg_substitution_ratio=0.0
    )
    
    res = solver.run()
    assert res["success"] is True
    assert "efficiencies" in res
    assert "CO2" in res["efficiencies"]
    assert "NOx" in res["efficiencies"]
    assert "block_strength_mpa" in res
    assert res["block_strength_mpa"] > 0.0


def test_crosslinking_increases_strength():
    """Verify that higher crosslinking density yields stronger structural blocks."""
    solver_normal = ExperimentalBiomineralizationSolver(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        nox_inlet_ppm=250.0,
        ca_concentration_mg_l=12.0,
        calcium_source_g_per_l=35.0,
        crosslinking_density=0.0,
        mg_substitution_ratio=0.0
    )
    res_normal = solver_normal.run()

    solver_crosslinked = ExperimentalBiomineralizationSolver(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        nox_inlet_ppm=250.0,
        ca_concentration_mg_l=12.0,
        calcium_source_g_per_l=35.0,
        crosslinking_density=0.8,
        mg_substitution_ratio=0.0
    )
    res_crosslinked = solver_crosslinked.run()

    assert res_crosslinked["block_strength_mpa"] > res_normal["block_strength_mpa"]


def test_magnesium_substitution_precipitation():
    """Verify magnesium substitution populates free Mg2+ and produces MgCO3."""
    solver = ExperimentalBiomineralizationSolver(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        nox_inlet_ppm=250.0,
        ca_concentration_mg_l=12.0,
        calcium_source_g_per_l=35.0,
        crosslinking_density=0.0,
        mg_substitution_ratio=0.5
    )
    res = solver.run()
    assert res["success"] is True
    assert res["final_state"]["MgCO3_s"] > 0.0
