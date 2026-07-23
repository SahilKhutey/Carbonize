"""
Hardware Engineering Spec Sheet & Unified Trust Score Generator.

Produces a formal engineering deliverable for pilot plant procurement,
reactor sizing handoff, and consumable schedule with unified confidence gating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class HardwareTrustScore:
    """Unified Confidence & Trust Score for Hardware Engineering Decisions."""
    trust_level: str                       # HIGH_VALIDATED, MODERATE_UNVALIDATED, LOW_HIGH_RISK
    provenance_status: str                 # BENCH_VALIDATED (🟢), LITERATURE_PLAUISBLE (🟡), ESTIMATED (🔴)
    comparator_status: str                 # VALIDATED, NEEDS_RECALIBRATION, SYSTEMATIC_BIAS, DISCREPANT
    ci_90_coverage_pct: float              # Empirical % of observations in p05-p95 band
    recommended_safety_margin_pct: float   # Sizing safety factor (+15% to +50%)
    hardware_guidance_text: str            # Direct engineering recommendation


@dataclass
class HardwareSpecSheet:
    """Formal Hardware Procurement & Reactor Sizing Deliverable."""
    project_name: str
    target_flue_gas_flow_nm3_hr: float
    target_co2_capture_pct: float
    
    # Sizing Specifications
    reactor_volume_m3: float
    column_diameter_m: float
    column_height_m: float
    residence_time_s: float
    liquid_to_gas_ratio_l_per_nm3: float
    
    # Applied Engineering Safety Factors
    applied_safety_margin_pct: float
    sized_reactor_volume_m3: float
    
    # Reagent & Consumables Schedule
    chitosan_wt_pct: float
    chitosan_consumption_kg_per_day: float
    ca_lime_consumption_kg_per_day: float
    ca_enzyme_dosage_mg_per_l: float
    mesh_replacement_interval_days: int
    
    # Trust Score & Gating
    trust_score: HardwareTrustScore
    notes: List[str] = field(default_factory=list)


class HardwareSpecSheetGenerator:
    """Generates Hardware Specification Sheets for Procurement & Sizing Handoff."""
    
    def generate(
        self,
        exhaust_flow_nm3_hr: float,
        target_co2_capture_pct: float = 85.0,
        residence_time_s: float = 27.0,
        liquid_to_gas_ratio: float = 8.5,
        chitosan_wt_pct: float = 3.0,
        ca_lime_wt_pct: float = 3.5,
        enzyme_dosage_mg_l: float = 12.0,
        comparator_result: Optional[Dict[str, Any]] = None,
        provenance_status: str = "🟡 Literature-derived",
    ) -> HardwareSpecSheet:
        """Generate a complete Hardware Specification Sheet."""
        
        # 1. Compute Base Geometry (assuming superficial gas velocity ~ 1.5 m/s)
        volumetric_flow_m3_s = (exhaust_flow_nm3_hr / 3600.0) * (313.15 / 273.15)
        superficial_velocity_m_s = 1.5
        
        cross_sectional_area = volumetric_flow_m3_s / superficial_velocity_m_s
        column_diameter = np.sqrt(4.0 * cross_sectional_area / np.pi)
        
        # Base Reactor Volume (V = Q * tau)
        base_volume_m3 = volumetric_flow_m3_s * residence_time_s
        column_height = base_volume_m3 / cross_sectional_area if cross_sectional_area > 0 else 5.0
        
        # 2. Evaluate Unified Trust Score & Gate Safety Margins
        comp_status = comparator_result.get("status", "UNTESTED") if comparator_result else "UNTESTED"
        coverage_pct = comparator_result.get("within_90pct_ci_pct", 0.0) if comparator_result else 0.0
        
        if comp_status == "VALIDATED" and coverage_pct >= 80.0:
            trust_level = "HIGH_CONFIDENCE_VALIDATED"
            safety_margin = 15.0
            guidance = "Model predictions match pilot bench data. Safe to proceed with standard +15% engineering margin."
        elif comp_status in ("NEEDS_RECALIBRATION", "OVERCONFIDENT_UQ"):
            trust_level = "MODERATE_UNVALIDATED_LITERATURE"
            safety_margin = 25.0
            guidance = "Moderate parameter uncertainty detected. Sizing updated with +25% residence time safety margin."
        elif comp_status in ("SYSTEMATIC_BIAS", "DISCREPANT_MODEL_UNRELIABLE"):
            trust_level = "LOW_HIGH_RISK_DISCREPANT"
            safety_margin = 50.0
            guidance = "HIGH RISK: Pilot data contradicts model kinetics. Apply +50% reactor volume buffer and re-calibrate."
        else:
            trust_level = "MODERATE_UNTESTED_LITERATURE"
            safety_margin = 30.0
            guidance = "Unvalidated baseline parameters. Apply conservative +30% safety margin pending CE-1 pilot data."
            
        trust_score = HardwareTrustScore(
            trust_level=trust_level,
            provenance_status=provenance_status,
            comparator_status=comp_status,
            ci_90_coverage_pct=coverage_pct,
            recommended_safety_margin_pct=safety_margin,
            hardware_guidance_text=guidance,
        )
        
        # 3. Apply Safety Margin to Reactor Sizing
        sized_volume_m3 = base_volume_m3 * (1.0 + safety_margin / 100.0)
        
        # 4. Consumables & Chemical Demand Calculations (24-hour operation)
        slurry_flow_l_min = (exhaust_flow_nm3_hr / 60.0) * (liquid_to_gas_ratio / 10.0)
        slurry_volume_m3_day = (slurry_flow_l_min * 60.0 * 24.0) / 1000.0
        
        chitosan_consumption_kg_day = slurry_volume_m3_day * 1010.0 * (chitosan_wt_pct / 100.0) * 0.05
        lime_consumption_kg_day = slurry_volume_m3_day * 1010.0 * (ca_lime_wt_pct / 100.0) * 0.20
        
        return HardwareSpecSheet(
            project_name="CBMS Pilot Unit Sizing Handoff",
            target_flue_gas_flow_nm3_hr=exhaust_flow_nm3_hr,
            target_co2_capture_pct=target_co2_capture_pct,
            reactor_volume_m3=round(base_volume_m3, 2),
            column_diameter_m=round(column_diameter, 2),
            column_height_m=round(column_height, 2),
            residence_time_s=residence_time_s,
            liquid_to_gas_ratio_l_per_nm3=liquid_to_gas_ratio,
            applied_safety_margin_pct=safety_margin,
            sized_reactor_volume_m3=round(sized_volume_m3, 2),
            chitosan_wt_pct=chitosan_wt_pct,
            chitosan_consumption_kg_per_day=round(chitosan_consumption_kg_day, 1),
            ca_lime_consumption_kg_per_day=round(lime_consumption_kg_day, 1),
            ca_enzyme_dosage_mg_per_l=enzyme_dosage_mg_l,
            mesh_replacement_interval_days=90,
            trust_score=trust_score,
            notes=[
                f"Sizing calculated for {exhaust_flow_nm3_hr} Nm3/hr exhaust flow.",
                f"Hardware safety factor of +{safety_margin}% applied to reactor volume based on trust score.",
                f"Modbus PLC control map defined in hardware/software-daq-edge-cloud.md."
            ]
        )
