"""Mass balance engine — extended with NOx and heavy-metals tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.results import KineticsResult
from cbms_shared.constants import MOLAR_MASSES, CPCB_SO2_LIMIT_MG_PER_NM3
from cbms_shared.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class MassBalanceResult:
    """Mass balance calculation result — all flows in kg/hr."""

    id: UUID = field(default_factory=uuid4)

    # -----------------------------------------------------------------------
    # Input streams [kg/hr]
    # -----------------------------------------------------------------------
    co2_input_kg_hr: float = 0.0
    so2_input_kg_hr: float = 0.0
    nox_input_kg_hr: float = 0.0          # NEW – combined NOx (NO + NO₂)
    fly_ash_input_kg_hr: float = 0.0
    metal_input_kg_hr: float = 0.0        # NEW – heavy metals entrained in fly ash
    ca_reagent_input_kg_hr: float = 0.0
    chitosan_input_kg_hr: float = 0.0
    air_baseline_kg_hr: float = 0.0

    # -----------------------------------------------------------------------
    # Output streams [kg/hr]
    # -----------------------------------------------------------------------
    caco3_output_kg_hr: float = 0.0
    gypsum_output_kg_hr: float = 0.0
    calcium_nitrate_output_kg_hr: float = 0.0   # NEW – Ca(NO₃)₂ from NOx absorption
    chelated_metal_output_kg_hr: float = 0.0    # NEW – heavy-metal chitosan chelate
    fly_ash_captured_kg_hr: float = 0.0
    chitosan_solid_kg_hr: float = 0.0
    bound_water_kg_hr: float = 0.0
    uncaptured_co2_kg_hr: float = 0.0
    uncaptured_so2_kg_hr: float = 0.0
    uncaptured_nox_kg_hr: float = 0.0           # NEW
    uncaptured_metal_kg_hr: float = 0.0         # NEW

    # -----------------------------------------------------------------------
    # Capture rates [%]
    # -----------------------------------------------------------------------
    co2_capture_pct: float = 0.0
    so2_capture_pct: float = 0.0
    nox_capture_pct: float = 0.0
    pm_capture_pct: float = 0.0
    metal_capture_pct: float = 0.0

    # -----------------------------------------------------------------------
    # Conservation & compliance
    # -----------------------------------------------------------------------
    conservation_error_pct: float = 0.0
    so2_outlet_mg_per_nm3: float = 0.0
    cpcb_so2_compliant: bool = True

    computation_time_s: float = 0.0


class MassBalanceEngine:
    """Computes steady-state mass flows for the capture system."""

    def compute(
        self,
        kinetics: KineticsResult,
        plant: PlantProfile,
        reagent: ReagentFormulation,
    ) -> MassBalanceResult:
        """Compute full mass balance including NOx and heavy-metal streams."""
        start = time.perf_counter()

        flow = float(plant.exhaust_flow_nm3_hr)
        molar_vol = 22.414e-3  # m³/mol at STP

        # -----------------------------------------------------------------------
        # INPUTS (kg/hr)
        # -----------------------------------------------------------------------
        co2_in = (flow * (float(plant.co2_vol_pct) / 100) * MOLAR_MASSES["CO2"] / molar_vol) / 1000.0
        so2_in = flow * float(plant.so2_mg_per_nm3) * 1e-6
        fly_ash_in = flow * float(plant.fly_ash_g_per_nm3) * 1e-3

        # NOx input: plant stores mg/Nm³; convert to kg/hr (treat as NO₂ for molar bookkeeping)
        nox_mg_per_nm3 = float(getattr(plant, "nox_mg_per_nm3", 0.0) or 0.0)
        nox_in = flow * nox_mg_per_nm3 * 1e-6  # kg/hr

        # Heavy metals entrained in fly ash (~0.15 % of fly-ash mass, typical coal)
        metal_frac_of_ash = 0.0015
        metal_in = fly_ash_in * metal_frac_of_ash

        # -----------------------------------------------------------------------
        # CAPTURE EFFICIENCIES (from kinetics)
        # -----------------------------------------------------------------------
        eff_co2  = kinetics.capture_efficiencies.get("co2_pct",   0.0) / 100.0
        eff_so2  = kinetics.capture_efficiencies.get("so2_pct",   0.0) / 100.0
        eff_nox  = kinetics.capture_efficiencies.get("nox_pct",   0.0) / 100.0
        eff_pm   = kinetics.capture_efficiencies.get("pm_pct",    0.0) / 100.0
        eff_metal = kinetics.capture_efficiencies.get("metal_pct", 0.0) / 100.0

        co2_captured  = co2_in  * eff_co2
        so2_captured  = so2_in  * eff_so2
        nox_captured  = nox_in  * eff_nox
        metal_captured = metal_in * eff_metal

        # -----------------------------------------------------------------------
        # STOICHIOMETRIC OUTPUTS
        # -----------------------------------------------------------------------
        # CO₂ → CaCO₃  (Ca(OH)₂ + CO₂ → CaCO₃ + H₂O)
        ca_for_co2    = co2_captured * (MOLAR_MASSES["CaOH2"] / MOLAR_MASSES["CO2"])
        caco3_out     = co2_captured * (MOLAR_MASSES["CaCO3"] / MOLAR_MASSES["CO2"])
        water_co2     = co2_captured * (MOLAR_MASSES["H2O"]   / MOLAR_MASSES["CO2"])

        # SO₂ → CaSO₄  (Ca(OH)₂ + SO₂ + ½O₂ → CaSO₄·2H₂O)
        ca_for_so2    = so2_captured * (MOLAR_MASSES["CaOH2"] / MOLAR_MASSES["SO2"])
        gypsum_out    = so2_captured * (MOLAR_MASSES["CaSO4"] / MOLAR_MASSES["SO2"])
        water_so2     = so2_captured * (MOLAR_MASSES["H2O"]   / MOLAR_MASSES["SO2"])
        oxygen_so2    = so2_captured * (16.0                  / MOLAR_MASSES["SO2"])

        # NOx → Ca(NO₃)₂  (2NO₂ + Ca(OH)₂ + ½O₂ → Ca(NO₃)₂ + H₂O)
        # Treat nox as NO₂ equivalent (M = 46.01 g/mol)
        ca_for_nox    = nox_captured * (MOLAR_MASSES["CaOH2"] / (2.0 * MOLAR_MASSES["NO2"]))
        ca_nitrate_out = nox_captured * (164.09 / (2.0 * MOLAR_MASSES["NO2"]))  # Ca(NO₃)₂ MW ≈ 164.09
        water_nox     = nox_captured * (MOLAR_MASSES["H2O"]   / (2.0 * MOLAR_MASSES["NO2"]))
        oxygen_nox    = nox_captured * (0.5 * MOLAR_MASSES["O2"] / (2.0 * MOLAR_MASSES["NO2"]))

        # Heavy metals → chitosan chelate (approximate 1:1 mass for bookkeeping)
        chelated_metal_out = metal_captured

        ca_reagent    = ca_for_co2 + ca_for_so2 + ca_for_nox

        # -----------------------------------------------------------------------
        # CHITOSAN MATRIX
        # -----------------------------------------------------------------------
        fly_ash_captured  = fly_ash_in * eff_pm
        dry_inorg = caco3_out + gypsum_out + ca_nitrate_out + fly_ash_captured
        chitosan  = dry_inorg * (float(reagent.chitosan_wt_pct) / 100.0)

        total_dry_solids = dry_inorg + chitosan
        water_bound = total_dry_solids * 0.15

        # -----------------------------------------------------------------------
        # MASS CONSERVATION CHECK
        # -----------------------------------------------------------------------
        # water_bound is an internal product term (not an external input), so it
        # must NOT appear in total_in. It is represented via the reaction-water terms.
        # uncaptured PM (fly_ash leaving via stack) must appear in total_out.
        total_in = (
            co2_in + so2_in + nox_in + fly_ash_in + metal_in
            + ca_reagent + chitosan
            + oxygen_so2 + oxygen_nox
        )
        total_out = (
            caco3_out + gypsum_out + ca_nitrate_out
            + chelated_metal_out + fly_ash_captured + chitosan
            + co2_in  * (1.0 - eff_co2)
            + so2_in  * (1.0 - eff_so2)
            + nox_in  * (1.0 - eff_nox)
            + metal_in * (1.0 - eff_metal)
            + fly_ash_in * (1.0 - eff_pm)   # uncaptured PM leaving via stack gas
            + water_co2 + water_so2 + water_nox
        )
        error_pct = abs(total_in - total_out) / total_in * 100.0 if total_in > 0 else 0.0


        # -----------------------------------------------------------------------
        # COMPLIANCE
        # -----------------------------------------------------------------------
        so2_outlet = (so2_in * (1.0 - eff_so2)) * 1e6 / flow if flow > 0 else 0.0
        cpcb_ok    = so2_outlet <= CPCB_SO2_LIMIT_MG_PER_NM3

        elapsed = time.perf_counter() - start

        return MassBalanceResult(
            co2_input_kg_hr=co2_in,
            so2_input_kg_hr=so2_in,
            nox_input_kg_hr=nox_in,
            fly_ash_input_kg_hr=fly_ash_in,
            metal_input_kg_hr=metal_in,
            ca_reagent_input_kg_hr=ca_reagent,
            chitosan_input_kg_hr=chitosan,
            air_baseline_kg_hr=0.0,
            caco3_output_kg_hr=caco3_out,
            gypsum_output_kg_hr=gypsum_out,
            calcium_nitrate_output_kg_hr=ca_nitrate_out,
            chelated_metal_output_kg_hr=chelated_metal_out,
            fly_ash_captured_kg_hr=fly_ash_captured,
            chitosan_solid_kg_hr=chitosan,
            bound_water_kg_hr=water_bound,
            uncaptured_co2_kg_hr=co2_in  * (1.0 - eff_co2),
            uncaptured_so2_kg_hr=so2_in  * (1.0 - eff_so2),
            uncaptured_nox_kg_hr=nox_in  * (1.0 - eff_nox),
            uncaptured_metal_kg_hr=metal_in * (1.0 - eff_metal),
            co2_capture_pct=eff_co2   * 100.0,
            so2_capture_pct=eff_so2   * 100.0,
            nox_capture_pct=eff_nox   * 100.0,
            pm_capture_pct=eff_pm     * 100.0,
            metal_capture_pct=eff_metal * 100.0,
            conservation_error_pct=error_pct,
            so2_outlet_mg_per_nm3=so2_outlet,
            cpcb_so2_compliant=cpcb_ok,
            computation_time_s=elapsed,
        )
