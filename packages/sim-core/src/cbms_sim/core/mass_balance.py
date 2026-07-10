"""
core/mass_balance.py
Implements the full multi-pollutant mass balance for a given plant profile.
Sums outputs from kinetics solver with fly-ash aggregate and reagent inputs.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from core.config import CONFIG, MOLAR, STD_TEMP, STD_PRESSURE


@dataclass
class MassBalanceResult:
    """Container for full system mass balance output."""
    # Inputs [kg/hr]
    co2_input: float
    so2_input: float
    fly_ash_input: float
    ca_reagent_input: float
    chitosan_input: float

    # Outputs [kg/hr]
    caco3_output: float
    gypsum_output: float
    fly_ash_captured: float
    chitosan_lattice: float
    bound_water: float
    captured_co2_total: float
    captured_so2_total: float

    # Mass conservation check
    total_input: float
    total_output: float
    mass_balance_error_pct: float

    # Compliance
    so2_emission_mg_per_nm3: float
    cpcb_compliant: bool


def compute_mass_balance(
    flow_nm3_per_hr: float,
    co2_vol_pct: float,
    so2_mg_per_nm3: float,
    fly_ash_g_per_nm3: float,
    enzyme_mg_per_l: float = 12.0,
    chitosan_wt_pct: float = 3.0,
    calcium_source: str = "Ca(OH)2",
    capture_efficiency_overrides: Optional[Dict[str, float]] = None,
) -> MassBalanceResult:
    """
    Compute the full steady-state mass balance.

    Args:
        flow_nm3_per_hr: Flue gas volumetric flow
        co2_vol_pct: CO2 concentration [vol%]
        so2_mg_per_nm3: SO2 concentration
        fly_ash_g_per_nm3: Particulate loading
        enzyme_mg_per_l: Carbonic anhydrase concentration
        chitosan_wt_pct: Chitosan weight percent in matrix
        calcium_source: "Ca(OH)2" | "Steel Slag" | "Waste Lime"
        capture_efficiency_overrides: Optional dict to override solver outputs

    Returns:
        MassBalanceResult with all input/output streams
    """
    # 1) GAS-PHASE INPUTS (kg/hr)
    # CO2: flow * vol_fraction * molar_mass / molar_volume
    molar_volume = 22.414e-3  # m³/mol at STP
    co2_input = (flow_nm3_per_hr * (co2_vol_pct / 100.0)
                 * MOLAR["CO2"] / molar_volume) / 1000.0

    # SO2: flow * concentration * 1e-6 (mg to kg)
    so2_input = flow_nm3_per_hr * so2_mg_per_nm3 * 1e-6

    # Fly ash
    fly_ash_input = flow_nm3_per_hr * fly_ash_g_per_nm3 * 1e-3

    # 2) APPLY CAPTURE EFFICIENCIES (from solver or override)
    if capture_efficiency_overrides is None:
        from core.kinetics import solve_reactor_kinetics
        kinetics_result = solve_reactor_kinetics(
            co2_vol_pct=co2_vol_pct,
            so2_mg_per_nm3=so2_mg_per_nm3,
            flow_nm3_per_hr=flow_nm3_per_hr,
            enzyme_mg_per_l=enzyme_mg_per_l,
            calcium_source_g_per_l=35.0,
        )
        eff_co2 = kinetics_result["co2_capture_efficiency_pct"] / 100.0
        eff_so2 = kinetics_result["so2_capture_efficiency_pct"] / 100.0
    else:
        eff_co2 = capture_efficiency_overrides.get("co2", 90.0) / 100.0
        eff_so2 = capture_efficiency_overrides.get("so2", 98.0) / 100.0

    captured_co2_total = co2_input * eff_co2
    captured_so2_total = so2_input * eff_so2

    # 3) STOICHIOMETRIC REAGENT CALCULATIONS
    # CO2 + Ca(OH)2 → CaCO3 + H2O
    ca_for_co2 = captured_co2_total * (MOLAR["CaOH2"] / MOLAR["CO2"])
    caco3_output = captured_co2_total * (MOLAR["CaCO3"] / MOLAR["CO2"])
    water_from_co2 = captured_co2_total * (MOLAR["H2O"] / MOLAR["CO2"])

    # SO2 + Ca(OH)2 + 0.5 O2 -> CaSO4 + H2O
    ca_for_so2 = captured_so2_total * (MOLAR["CaOH2"] / MOLAR["SO2"])
    gypsum_output = captured_so2_total * (MOLAR["CaSO4"] / MOLAR["SO2"])
    water_from_so2 = captured_so2_total * (MOLAR["H2O"] / MOLAR["SO2"])
    oxygen_for_so2 = captured_so2_total * (16.0 / MOLAR["SO2"])

    # 4) TOTAL REAGENT CONSUMPTION
    ca_reagent_input = ca_for_co2 + ca_for_so2

    # 5) CHITOSAN MATRIX DEMAND (3% of dry inorganic solids)
    fly_ash_captured = fly_ash_input  # 100% capture in Stage 1
    dry_inorganic = caco3_output + gypsum_output + fly_ash_captured
    chitosan_lattice = dry_inorganic * (chitosan_wt_pct / 100.0)

    # Total dry solids output
    total_dry_solids = caco3_output + gypsum_output + fly_ash_captured + chitosan_lattice

    # Bound hydration water (assumed 15% of dry solids mass)
    bound_water = total_dry_solids * 0.15

    # 6) TOTAL INPUTS / OUTPUTS BALANCE
    total_input = (
        co2_input + so2_input + fly_ash_input +
        ca_reagent_input + chitosan_lattice + bound_water + oxygen_for_so2
    )
    total_output = (
        caco3_output + gypsum_output + fly_ash_captured +
        chitosan_lattice + bound_water +
        (co2_input - captured_co2_total) +  # Uncaptured CO2 to atmosphere
        (so2_input - captured_so2_total) +  # Uncaptured SO2 to atmosphere
        water_from_co2 + water_from_so2
    )

    mass_balance_error_pct = (
        abs(total_input - total_output) / total_input * 100.0
        if total_input > 0 else 0.0
    )

    # 7) REGULATORY COMPLIANCE
    uncaptured_so2_kg_hr = so2_input - captured_so2_total
    uncaptured_so2_mg_nm3 = (uncaptured_so2_kg_hr * 1e6) / flow_nm3_per_hr
    cpcb_compliant = uncaptured_so2_mg_nm3 <= CONFIG.materials.CPCB_SO2_LIMIT

    # Effective input to flux (avoid unused warning)
    _ = (ca_for_co2, ca_for_so2, water_from_co2, water_from_so2)

    return MassBalanceResult(
        co2_input=co2_input,
        so2_input=so2_input,
        fly_ash_input=fly_ash_input,
        ca_reagent_input=ca_reagent_input,
        chitosan_input=chitosan_lattice,
        caco3_output=caco3_output,
        gypsum_output=gypsum_output,
        fly_ash_captured=fly_ash_captured,
        chitosan_lattice=chitosan_lattice,
        bound_water=bound_water,
        captured_co2_total=captured_co2_total,
        captured_so2_total=captured_so2_total,
        total_input=total_input,
        total_output=total_output,
        mass_balance_error_pct=mass_balance_error_pct,
        so2_emission_mg_per_nm3=uncaptured_so2_mg_nm3,
        cpcb_compliant=cpcb_compliant,
    )
