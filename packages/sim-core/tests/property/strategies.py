"""
Custom Hypothesis strategies for generating valid sim-core inputs.

These strategies respect the physical constraints of the simulation.
"""

from hypothesis import strategies as st
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timezone

from cbms_sim.v1.types import (
    PlantProfile, ReagentFormulation, OperatingConditions,
    SimulationRequest, SimulationOptions, SimulationType,
    BoilerType, CalciumSourceType,
)

# =============================================================================
# PHYSICAL PARAMETER STRATEGIES
# =============================================================================

# Concentrations and rates must be positive
positive_float = st.floats(
    min_value=1e-10,
    max_value=1e10,
    allow_nan=False,
    allow_infinity=False,
)

# Non-negative quantities
nonnegative_float = st.floats(
    min_value=0.0,
    max_value=1e10,
    allow_nan=False,
    allow_infinity=False,
)

# Temperature in Celsius (operational range)
temperature_c = st.floats(
    min_value=10.0,    # Minimum operating
    max_value=80.0,    # Maximum operating
    allow_nan=False,
    allow_infinity=False,
)

# pH (operational range for our system)
ph_value = st.floats(
    min_value=5.0,
    max_value=11.0,
    allow_nan=False,
    allow_infinity=False,
)

# L/G ratio (typical FGD range)
lg_ratio = st.floats(
    min_value=3.0,
    max_value=20.0,
    allow_nan=False,
    allow_infinity=False,
)

# Residence time (seconds)
residence_time = st.floats(
    min_value=5.0,
    max_value=120.0,
    allow_nan=False,
    allow_infinity=False,
)

# CO2 concentration (vol% in dry flue gas)
co2_vol_pct = st.floats(
    min_value=0.1,
    max_value=25.0,
    allow_nan=False,
    allow_infinity=False,
)

# SO2 concentration (mg/Nm3)
so2_mg_per_nm3 = st.floats(
    min_value=0.0,
    max_value=10_000.0,
    allow_nan=False,
    allow_infinity=False,
)

# NOx concentration (mg/Nm3)
nox_mg_per_nm3 = st.floats(
    min_value=0.0,
    max_value=3_000.0,
    allow_nan=False,
    allow_infinity=False,
)

# Fly ash (g/Nm3)
fly_ash_g_per_nm3 = st.floats(
    min_value=0.0,
    max_value=500.0,
    allow_nan=False,
    allow_infinity=False,
)

# Exhaust flow (Nm3/hr) - wide range from small industry to large power plant
exhaust_flow = st.floats(
    min_value=100.0,
    max_value=500_000.0,
    allow_nan=False,
    allow_infinity=False,
)

# Chitosan wt% (operational range)
chitosan_pct = st.floats(
    min_value=0.5,
    max_value=6.0,
    allow_nan=False,
    allow_infinity=False,
)

# Ca source wt%
ca_pct = st.floats(
    min_value=1.0,
    max_value=10.0,
    allow_nan=False,
    allow_infinity=False,
)

# Enzyme loading (mg/L)
enzyme_mg_per_l = st.floats(
    min_value=0.1,
    max_value=50.0,
    allow_nan=False,
    allow_infinity=False,
)

# Heavy metal concentration (ug/Nm3)
heavy_metal_conc = st.floats(
    min_value=0.0,
    max_value=500.0,
    allow_nan=False,
    allow_infinity=False,
)

# Initial state vector for ODE (9 species, all non-negative)
initial_state = st.lists(
    st.floats(min_value=0.0, max_value=200.0, allow_nan=False, allow_infinity=False),
    min_size=9,
    max_size=9,
).map(list)

# =============================================================================
# PARAMETER STRATEGIES
# =============================================================================

@st.composite
def kinetic_parameters(draw) -> dict:
    """Generate physically realistic kinetic parameters."""
    return {
        "k_cat": draw(st.floats(min_value=1e5, max_value=1e7, allow_nan=False)),
        "K_M_co2": draw(st.floats(min_value=0.1e-3, max_value=100e-3, allow_nan=False)),
        "k_inact": draw(st.floats(min_value=1e-7, max_value=1e-3, allow_nan=False)),
        "E_a_inact": draw(st.floats(min_value=30e3, max_value=200e3, allow_nan=False)),
        "k_so2": draw(st.floats(min_value=1e-4, max_value=0.1, allow_nan=False)),
        "k_chel": draw(st.floats(min_value=1e-4, max_value=0.1, allow_nan=False)),
        "ca_cl2": draw(st.floats(min_value=0.001, max_value=1.0, allow_nan=False)),
        "pH_initial": draw(ph_value),
        "T_reactor": draw(st.floats(min_value=283.15, max_value=353.15, allow_nan=False)),  # 10-80°C
    }

# =========================================================================================
# DOMAIN OBJECT STRATEGIES
# =========================================================================================

@st.composite
def plant_profile_strategy(draw) -> PlantProfile:
    """Generate a valid PlantProfile with random but valid data."""
    return PlantProfile(
        id=uuid4(),
        name=draw(st.text(min_size=1, max_size=100)),
        location=draw(st.text(min_size=0, max_size=100)),
        boiler_type=draw(st.sampled_from(list(BoilerType))),
        exhaust_flow_nm3_hr=Decimal(str(round(draw(exhaust_flow), 2))),
        baseline_temperature_c=Decimal(str(round(draw(st.floats(50, 300, allow_nan=False)), 1))),
        co2_vol_pct=Decimal(str(round(draw(co2_vol_pct), 2))),
        so2_mg_per_nm3=Decimal(str(round(draw(so2_mg_per_nm3), 1))),
        nox_mg_per_nm3=Decimal(str(round(draw(nox_mg_per_nm3), 1))),
        fly_ash_g_per_nm3=Decimal(str(round(draw(fly_ash_g_per_nm3), 2))),
        heavy_metal_profile=draw(st.lists(
            st.fixed_dictionaries({
                "element": st.sampled_from(["Hg", "Pb", "Cd", "As"]),
                "conc_ug_per_nm3": heavy_metal_conc,
            }),
            min_size=0,
            max_size=4,
        )),
        operating_hours_per_year=draw(st.integers(min_value=1000, max_value=8760)),
    )

@st.composite
def reagent_formulation_strategy(draw) -> ReagentFormulation:
    """Generate a valid ReagentFormulation with random but valid data."""
    return ReagentFormulation(
        id=uuid4(),
        name=draw(st.text(min_size=1, max_size=100)),
        chitosan_wt_pct=Decimal(str(round(draw(chitosan_pct), 2))),
        ca_source_type=draw(st.sampled_from(list(CalciumSourceType))),
        ca_wt_pct=Decimal(str(round(draw(ca_pct), 2))),
        enzyme_mg_per_l=Decimal(str(round(draw(enzyme_mg_per_l), 2))),
    )

@st.composite
def operating_conditions_strategy(draw) -> OperatingConditions:
    """Generate valid OperatingConditions."""
    return OperatingConditions(
        reactor_temp_c=Decimal(str(round(draw(temperature_c), 1))),
        pH_initial=Decimal(str(round(draw(ph_value), 2))),
        liquid_to_gas_ratio=Decimal(str(round(draw(lg_ratio), 2))),
        residence_time_s=Decimal(str(round(draw(residence_time), 1))),
        mesh_count=draw(st.integers(min_value=1, max_value=20)),
        press_force_bar=Decimal(str(round(draw(st.floats(50, 500, allow_nan=False)), 1))),
        curing_temperature_c=Decimal(str(round(draw(st.floats(15, 50, allow_nan=False)), 1))),
        curing_time_h=Decimal(str(round(draw(st.floats(6, 168, allow_nan=False)), 1))),
    )

@st.composite
def simulation_request_strategy(draw) -> SimulationRequest:
    """Generate a complete valid SimulationRequest."""
    return SimulationRequest(
        request_id=uuid4(),
        org_id=uuid4(),
        user_id=uuid4(),
        plant=draw(plant_profile_strategy()),
        reagent=draw(reagent_formulation_strategy()),
        conditions=draw(operating_conditions_strategy()),
        options=SimulationOptions(
            simulation_type=SimulationType.BASELINE,
            n_mc_samples=100,
            random_seed=draw(st.one_of(st.none(), st.integers(min_value=0, max_value=2**32))),
            timeout_seconds=draw(st.integers(min_value=60, max_value=3600)),
        ),
        submitted_at=datetime.now(timezone.utc),
        parameter_set_version="v2026.1",
        code_version="0.1.0",
    )
