"""Mass balance engine."""

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
    """Mass balance calculation result."""
    
    id: UUID = field(default_factory=uuid4)
    
    # Input streams [kg/hr]
    co2_input_kg_hr: float = 0.0
    so2_input_kg_hr: float = 0.0
    fly_ash_input_kg_hr: float = 0.0
    ca_reagent_input_kg_hr: float = 0.0
    chitosan_input_kg_hr: float = 0.0
    air_baseline_kg_hr: float = 0.0
    
    # Output streams [kg/hr]
    caco3_output_kg_hr: float = 0.0
    gypsum_output_kg_hr: float = 0.0
    fly_ash_captured_kg_hr: float = 0.0
    chitosan_solid_kg_hr: float = 0.0
    bound_water_kg_hr: float = 0.0
    uncaptured_co2_kg_hr: float = 0.0
    uncaptured_so2_kg_hr: float = 0.0
    
    # Capture rates [%]
    co2_capture_pct: float = 0.0
    so2_capture_pct: float = 0.0
    pm_capture_pct: float = 0.0
    metal_capture_pct: float = 0.0
    
    # Conservation & compliance
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
        """Compute full mass balance."""
        start = time.perf_counter()
        
        flow = float(plant.exhaust_flow_nm3_hr)
        molar_vol = 22.414e-3  # m³/mol at STP
        
        # INPUTS (kg/hr)
        co2_in = (flow * (float(plant.co2_vol_pct) / 100) * MOLAR_MASSES["CO2"] / molar_vol) / 1000.0
        so2_in = flow * float(plant.so2_mg_per_nm3) * 1e-6
        fly_ash_in = flow * float(plant.fly_ash_g_per_nm3) * 1e-3
        
        # CAPTURE RATES (from kinetics)
        eff_co2 = kinetics.capture_efficiencies.get("co2_pct", 0.0) / 100
        eff_so2 = kinetics.capture_efficiencies.get("so2_pct", 0.0) / 100
        eff_pm = kinetics.capture_efficiencies.get("pm_pct", 0.0) / 100
        eff_metal = kinetics.capture_efficiencies.get("metal_pct", 0.0) / 100
        
        co2_captured = co2_in * eff_co2
        so2_captured = so2_in * eff_so2
        
        # STOICHIOMETRIC REAGENTS
        ca_for_co2 = co2_captured * (MOLAR_MASSES["CaOH2"] / MOLAR_MASSES["CO2"])
        caco3_out = co2_captured * (MOLAR_MASSES["CaCO3"] / MOLAR_MASSES["CO2"])
        water_from_co2 = co2_captured * (MOLAR_MASSES["H2O"] / MOLAR_MASSES["CO2"])
        
        ca_for_so2 = so2_captured * (MOLAR_MASSES["CaOH2"] / MOLAR_MASSES["SO2"])
        gypsum_out = so2_captured * (MOLAR_MASSES["CaSO4"] / MOLAR_MASSES["SO2"])
        water_from_so2 = so2_captured * (MOLAR_MASSES["H2O"] / MOLAR_MASSES["SO2"])
        oxygen_for_so2 = so2_captured * (16.0 / MOLAR_MASSES["SO2"])
        
        ca_reagent = ca_for_co2 + ca_for_so2
        
        # CHITOSAN MATRIX
        fly_ash_captured = fly_ash_in
        dry_inorg = caco3_out + gypsum_out + fly_ash_captured
        chitosan = dry_inorg * (float(reagent.chitosan_wt_pct) / 100.0)
        
        total_dry_solids = caco3_out + gypsum_out + fly_ash_captured + chitosan
        water_bound = total_dry_solids * 0.15
        
        # CONSERVATION
        total_in = co2_in + so2_in + fly_ash_in + ca_reagent + chitosan + water_bound + oxygen_for_so2
        total_out = (
            caco3_out + gypsum_out + fly_ash_captured + chitosan + water_bound +
            co2_in * (1.0 - eff_co2) + so2_in * (1.0 - eff_so2) +
            water_from_co2 + water_from_so2
        )
        error_pct = abs(total_in - total_out) / total_in * 100 if total_in > 0 else 0
        
        # COMPLIANCE
        so2_outlet = (so2_in * (1.0 - eff_so2)) * 1e6 / flow if flow > 0 else 0
        cpcb_ok = so2_outlet <= CPCB_SO2_LIMIT_MG_PER_NM3
        
        elapsed = time.perf_counter() - start
        
        return MassBalanceResult(
            co2_input_kg_hr=co2_in,
            so2_input_kg_hr=so2_in,
            fly_ash_input_kg_hr=fly_ash_in,
            ca_reagent_input_kg_hr=ca_reagent,
            chitosan_input_kg_hr=chitosan,
            air_baseline_kg_hr=0.0,
            caco3_output_kg_hr=caco3_out,
            gypsum_output_kg_hr=gypsum_out,
            fly_ash_captured_kg_hr=fly_ash_captured,
            chitosan_solid_kg_hr=chitosan,
            bound_water_kg_hr=water_bound,
            uncaptured_co2_kg_hr=co2_in * (1.0 - eff_co2),
            uncaptured_so2_kg_hr=so2_in * (1.0 - eff_so2),
            co2_capture_pct=eff_co2 * 100.0,
            so2_capture_pct=eff_so2 * 100.0,
            pm_capture_pct=eff_pm * 100.0,
            metal_capture_pct=eff_metal * 100.0,
            conservation_error_pct=error_pct,
            so2_outlet_mg_per_nm3=so2_outlet,
            cpcb_so2_compliant=cpcb_ok,
            computation_time_s=elapsed
        )
