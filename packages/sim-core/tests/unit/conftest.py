"""Shared fixtures for sim-core unit tests."""

from decimal import Decimal
from pathlib import Path
import pytest
import numpy as np

from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation, CalciumSourceType
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.kinetics.engine import KineticsEngine
from cbms_sim.domain.parameters.registry import ParameterRegistry


@pytest.fixture(scope="session")
def param_registry() -> ParameterRegistry:
    """Load the production parameter registry."""
    return ParameterRegistry.from_file(
        Path(__file__).parent.parent.parent.parent.parent / "data" / "parameters" / "v2026.1.json"
    )


@pytest.fixture
def sample_plant() -> PlantProfile:
    """Standard Indian coal-fired power plant profile."""
    return PlantProfile(
        id="00000000-0000-0000-0000-000000000001",
        name="Standard Test Plant",
        location="Maharashtra",
        boiler_type="pulverized_coal",
        exhaust_flow_nm3_hr=Decimal("10000.0"),
        baseline_temperature_c=Decimal("150.0"),
        co2_vol_pct=Decimal("14.0"),
        so2_mg_per_nm3=Decimal("1200.0"),
        nox_mg_per_nm3=Decimal("500.0"),
        fly_ash_g_per_nm3=Decimal("45.0"),
        heavy_metal_profile=[
            {"element": "Hg", "conc_ug_per_nm3": 5.0},
            {"element": "Pb", "conc_ug_per_nm3": 50.0},
        ],
        operating_hours_per_year=8000,
    )


@pytest.fixture
def sample_reagent() -> ReagentFormulation:
    """Standard 3% chitosan / 0.5M Ca / 12 mg/L CA."""
    return ReagentFormulation(
        id="00000000-0000-0000-0000-000000000002",
        name="Standard 3% Chitosan",
        chitosan_wt_pct=Decimal("3.0"),
        ca_source_type=CalciumSourceType.LIME,
        ca_wt_pct=Decimal("3.5"),
        enzyme_mg_per_l=Decimal("12.0"),
        enzyme_type="bovine_CA",
    )


@pytest.fixture
def sample_conditions() -> OperatingConditions:
    """Standard operating conditions."""
    return OperatingConditions(
        reactor_temp_c=Decimal("40.0"),
        pH_initial=Decimal("8.5"),
        liquid_to_gas_ratio=Decimal("8.5"),
        residence_time_s=Decimal("27.0"),
        mesh_count=6,
        press_force_bar=Decimal("200.0"),
        curing_temperature_c=Decimal("25.0"),
        curing_time_h=Decimal("48.0"),
    )


@pytest.fixture(scope="session")
def kinetics_engine() -> KineticsEngine:
    """Warmed-up kinetics engine for solver tests."""
    engine = KineticsEngine()
    engine.warmup()
    return engine


@pytest.fixture
def standard_initial_state() -> np.ndarray:
    """Initial state for standard conditions (9 species)."""
    return np.array([
        10.0,    # [0] CO2_aq
        1.0,     # [1] HCO3
        100.0,   # [2] Ca2
        0.0,     # [3] CaCO3_s
        0.5,     # [4] SO2_aq
        0.0,     # [5] CaSO4_s
        12.0,    # [6] CA_active
        0.0,     # [7] Metal_chel
        0.0,     # [8] PM_trapped
    ])


@pytest.fixture
def standard_params() -> dict:
    """Standard parameters for ODE solver."""
    return {
        "k_cat": 1.0e6,
        "K_M_co2": 8.5e-3,
        "k_inact": 5.0e-5,
        "E_a_inact": 85.0e3,
        "k_so2": 2.5e-2,
        "k_chel": 8.0e-3,
        "ca_cl2": 0.5 * 1000.0 / 74.10,
        "pH_initial": 8.5,
        "T_reactor": 40.0 + 273.15,
    }


@pytest.fixture
def rtol() -> float:
    """Relative tolerance for floating-point comparisons."""
    return 1e-6


@pytest.fixture
def atol() -> float:
    """Absolute tolerance for floating-point comparisons."""
    return 1e-9
