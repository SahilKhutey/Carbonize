"""
Pollutants Database & System Impact Assessment FastAPI Router.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID

from cbms_sim.domain.pollutants import POLLUTANT_DATABASE, PollutantsAssessor
from cbms_api.middleware.rate_limiting import rate_limit_write
from cbms_api.api.dependencies import get_active_tenant_id

router = APIRouter(prefix="/api/pollutants", tags=["pollutants"])


class ImpactAssessmentRequest(BaseModel):
    co2_vol_pct: float = Field(default=14.0, ge=1.0, le=40.0)
    so2_mg_per_nm3: float = Field(default=650.0, ge=0.0, le=5000.0)
    nox_mg_per_nm3: float = Field(default=450.0, ge=0.0, le=3000.0)
    fly_ash_g_per_nm3: float = Field(default=25.0, ge=0.0, le=200.0)
    exhaust_flow_nm3_hr: float = Field(default=10000.0, ge=100.0, le=100000.0)


@router.get("/database")
async def get_pollutants_database(org_id: UUID = Depends(get_active_tenant_id)):
    """
    Get authoratative chemical, thermodynamic, and statutory regulatory properties for all pollutants.
    """
    return {
        key: {
            "id": prop.id,
            "name": prop.name,
            "formula": prop.formula,
            "molar_mass_g_per_mol": prop.molar_mass_g_per_mol,
            "henry_constant_mol_per_m3_pa": prop.henry_constant_mol_per_m3_pa,
            "diffusivity_m2_per_s": prop.diffusivity_m2_per_s,
            "cpcb_limit_mg_per_nm3": prop.cpcb_limit_mg_per_nm3,
            "usepa_limit_mg_per_nm3": prop.usepa_limit_mg_per_nm3,
            "primary_system_impact": prop.primary_system_impact,
            "control_method": prop.control_method,
        }
        for key, prop in POLLUTANT_DATABASE.items()
    }


@router.post("/assess-impact")
@rate_limit_write(limit="30/minute")
async def assess_pollutant_impact(
    request: Request,
    body: ImpactAssessmentRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Evaluate real-time system impact, enzyme inactivation acceleration, scaling risk, and control actions.
    """
    assessor = PollutantsAssessor()
    res = assessor.assess_impact(
        co2_vol_pct=body.co2_vol_pct,
        so2_mg_per_nm3=body.so2_mg_per_nm3,
        nox_mg_per_nm3=body.nox_mg_per_nm3,
        fly_ash_g_per_nm3=body.fly_ash_g_per_nm3,
        exhaust_flow_nm3_hr=body.exhaust_flow_nm3_hr,
    )
    return {
        "ph_drop_rate_per_min": res.ph_drop_rate_per_min,
        "ca_enzyme_inactivation_acceleration_factor": res.ca_enzyme_inactivation_acceleration_factor,
        "caso4_scaling_risk_index": res.caso4_scaling_risk_index,
        "chitosan_active_site_depletion_pct": res.chitosan_active_site_depletion_pct,
        "recommended_lime_dosing_kg_per_hr": res.recommended_lime_dosing_kg_per_hr,
        "recommended_control_actions": res.recommended_control_actions,
    }
