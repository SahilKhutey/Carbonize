"""
Pollutants Chemistry Database & System Impact Assessor.

Provides authoritative physical, thermodynamic, and toxicological properties
for industrial flue gas pollutants, evaluates system degradation risks (enzyme
inactivation, scaling, corrosion, active site depletion), and recommends
control remediation strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass(frozen=True)
class PollutantProperty:
    """Authoritative physical & regulatory properties for a flue gas pollutant."""
    id: str
    name: str
    formula: str
    molar_mass_g_per_mol: float
    henry_constant_mol_per_m3_pa: float     # at 25°C
    diffusivity_m2_per_s: float             # in water at 25°C
    cpcb_limit_mg_per_nm3: float            # CPCB Indian statutory limit
    usepa_limit_mg_per_nm3: float           # USEPA statutory limit
    primary_system_impact: str              # e.g., Slurry Acidification, Enzyme Inactivation
    control_method: str                     # e.g., CA Enzymatic Hydration, Chitosan Chelation


@dataclass
class ImpactAssessmentResult:
    """Quantitative assessment of flue gas pollutant impact on CBMS reactor system."""
    ph_drop_rate_per_min: float
    ca_enzyme_inactivation_acceleration_factor: float
    caso4_scaling_risk_index: float           # 0.0 (low) to 1.0 (severe)
    chitosan_active_site_depletion_pct: float
    recommended_lime_dosing_kg_per_hr: float
    recommended_control_actions: List[str] = field(default_factory=list)


POLLUTANT_DATABASE: Dict[str, PollutantProperty] = {
    "CO2": PollutantProperty(
        id="CO2",
        name="Carbon Dioxide",
        formula="CO₂",
        molar_mass_g_per_mol=44.01,
        henry_constant_mol_per_m3_pa=3.3e-4,
        diffusivity_m2_per_s=1.92e-9,
        cpcb_limit_mg_per_nm3=150000.0,       # 15 Vol % benchmark
        usepa_limit_mg_per_nm3=150000.0,
        primary_system_impact="Forms carbonic acid (H₂CO₃), driving bicarbonate hydration and calcite biomineralization.",
        control_method="Carbonic Anhydrase (CA) enzymatic catalysis + Lime [Ca(OH)₂] slurry precipitation.",
    ),
    "SO2": PollutantProperty(
        id="SO2",
        name="Sulfur Dioxide",
        formula="SO₂",
        molar_mass_g_per_mol=64.06,
        henry_constant_mol_per_m3_pa=1.32e-2,
        diffusivity_m2_per_s=1.45e-9,
        cpcb_limit_mg_per_nm3=200.0,          # TPP CPCB norm
        usepa_limit_mg_per_nm3=150.0,
        primary_system_impact="Causes rapid slurry acidification (sulfurous/sulfuric acid), deactivates CA enzymes below pH 6.5, and forms Gypsum (CaSO₄·2H₂O) wall scale.",
        control_method="Alkalinity buffering (Ca(OH)₂ feed) + Gypsum crystal nucleation control.",
    ),
    "NOx": PollutantProperty(
        id="NOx",
        name="Nitrogen Oxides (NO₂ equiv)",
        formula="NO_x",
        molar_mass_g_per_mol=46.01,
        henry_constant_mol_per_m3_pa=6.7e-3,
        diffusivity_m2_per_s=1.60e-9,
        cpcb_limit_mg_per_nm3=300.0,          # TPP CPCB norm
        usepa_limit_mg_per_nm3=200.0,
        primary_system_impact="Forms nitric acid (HNO₃), oxidizes active enzyme residues, and reacts with Calcium to form Calcium Nitrate [Ca(NO₃)₂] fertilizer.",
        control_method="Oxidative bio-absorption into Calcium Nitrate agricultural resource stream.",
    ),
    "PM": PollutantProperty(
        id="PM",
        name="Particulate Matter / Fly Ash",
        formula="PM₂.₅/PM₁₀",
        molar_mass_g_per_mol=60.08,           # Silica/alumina equivalent
        henry_constant_mol_per_m3_pa=0.0,     # Insoluble solid
        diffusivity_m2_per_s=0.0,
        cpcb_limit_mg_per_nm3=30.0,           # Strict CPCB PM norm
        usepa_limit_mg_per_nm3=20.0,
        primary_system_impact="Causes mechanical abrasion of packing media, increases column ΔP, and physically blocks enzyme active pockets.",
        control_method="Structured stainless-steel mesh filtration + ultrasonic pulse cleaning.",
    ),
    "Pb": PollutantProperty(
        id="Pb",
        name="Lead",
        formula="Pb²⁺",
        molar_mass_g_per_mol=207.2,
        henry_constant_mol_per_m3_pa=0.0,
        diffusivity_m2_per_s=0.95e-9,
        cpcb_limit_mg_per_nm3=0.5,
        usepa_limit_mg_per_nm3=0.1,
        primary_system_impact="Heavy metal toxicity, inhibits enzyme active sites via thiol binding.",
        control_method="Chitosan biopolymer amine chelation matrix.",
    ),
    "Hg": PollutantProperty(
        id="Hg",
        name="Mercury",
        formula="Hg²⁺",
        molar_mass_g_per_mol=200.59,
        henry_constant_mol_per_m3_pa=0.0,
        diffusivity_m2_per_s=0.85e-9,
        cpcb_limit_mg_per_nm3=0.03,
        usepa_limit_mg_per_nm3=0.015,
        primary_system_impact="Severe catalytic poison, irreversibly deactivates zinc active site in CA enzymes.",
        control_method="Crosslinked glutaraldehyde-chitosan complexation.",
    ),
}


class PollutantsAssessor:
    """Evaluates multi-pollutant system impacts and recommends control strategies."""

    def assess_impact(
        self,
        co2_vol_pct: float = 14.0,
        so2_mg_per_nm3: float = 650.0,
        nox_mg_per_nm3: float = 450.0,
        fly_ash_g_per_nm3: float = 25.0,
        exhaust_flow_nm3_hr: float = 10000.0,
    ) -> ImpactAssessmentResult:
        """Perform quantitative impact assessment on reactor kinetics and hardware."""
        
        # 1. Acidification Rate Calculation (SO2 + NOx contribute strong acid)
        so2_molar_rate = (exhaust_flow_nm3_hr * so2_mg_per_nm3 * 1e-6) / 64.06  # kmol/hr
        nox_molar_rate = (exhaust_flow_nm3_hr * nox_mg_per_nm3 * 1e-6) / 46.01  # kmol/hr
        
        total_acid_kmol_hr = 2.0 * so2_molar_rate + nox_molar_rate
        ph_drop_rate = min(2.5, total_acid_kmol_hr * 0.15)
        
        # 2. Enzyme Deactivation Acceleration Factor
        # High SO2 (> 500 mg/Nm3) drops pH, accelerating thermal deactivation by up to 3x
        deact_factor = 1.0
        if so2_mg_per_nm3 > 500.0:
            deact_factor += 0.002 * (so2_mg_per_nm3 - 500.0)
            
        # 3. Gypsum Scaling Risk Index
        scaling_index = min(1.0, (so2_mg_per_nm3 / 1000.0) * (co2_vol_pct / 15.0))
        
        # 4. Chitosan Active Site Depletion
        heavy_metal_est_mg_hr = fly_ash_g_per_nm3 * exhaust_flow_nm3_hr * 0.0015
        site_depletion_pct = min(100.0, (heavy_metal_est_mg_hr / 500.0) * 100.0)
        
        # 5. Required Lime Dosing Rate (kg/hr) for Stoichiometric Neutralization
        lime_dosing_kg_hr = (so2_molar_rate * 74.09) + (nox_molar_rate * 0.5 * 74.09) + (co2_vol_pct * exhaust_flow_nm3_hr * 0.002)
        
        # 6. Actionable Control Recommendations
        actions = []
        if so2_mg_per_nm3 > POLLUTANT_DATABASE["SO2"].cpcb_limit_mg_per_nm3:
            actions.append(f"CRITICAL: Inlet SO₂ ({so2_mg_per_nm3} mg/Nm³) exceeds CPCB limit (200 mg/Nm³). Increase Ca(OH)₂ lime slurry feed to {lime_dosing_kg_hr:.1f} kg/hr.")
        if ph_drop_rate > 0.5:
            actions.append("pH drop rate exceeds 0.5 units/min. Enable automatic alkaline buffer dosing.")
        if scaling_index > 0.6:
            actions.append("High Gypsum (CaSO₄) wall-scaling risk detected. Initiate ultrasonic mesh backflush every 48 hours.")
        if site_depletion_pct > 50.0:
            actions.append("Chitosan amine chelation site depletion > 50%. Schedule biopolymer matrix replenishment.")

        if not actions:
            actions.append("All flue gas pollutants within baseline operating envelope. System status: OPTIMAL.")

        return ImpactAssessmentResult(
            ph_drop_rate_per_min=round(ph_drop_rate, 3),
            ca_enzyme_inactivation_acceleration_factor=round(deact_factor, 2),
            caso4_scaling_risk_index=round(scaling_index, 2),
            chitosan_active_site_depletion_pct=round(site_depletion_pct, 1),
            recommended_lime_dosing_kg_per_hr=round(lime_dosing_kg_hr, 1),
            recommended_control_actions=actions,
        )
