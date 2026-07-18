"""
experimental.py
FastAPI router for experimental CCUS chemistry features.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from cbms_sim.core.experimental_chemistry import ExperimentalBiomineralizationSolver
from cbms_api.middleware.rate_limiting import rate_limit_write
from cbms_api.api.dependencies import get_active_tenant_id
from uuid import UUID

router = APIRouter(prefix="/experimental", tags=["Experimental"])


class ExperimentalSimRequest(BaseModel):
    co2_vol_pct: float = Field(default=14.0, ge=0.0, le=100.0)
    so2_mg_per_nm3: float = Field(default=1200.0, ge=0.0)
    nox_inlet_ppm: float = Field(default=250.0, ge=0.0)
    ca_concentration_mg_l: float = Field(default=12.0, ge=0.0)
    calcium_source_g_per_l: float = Field(default=35.0, ge=0.0)
    crosslinking_density: float = Field(default=0.5, ge=0.0, le=1.0)
    mg_substitution_ratio: float = Field(default=0.3, ge=0.0, le=1.0)


@router.post("/simulate")
@rate_limit_write(limit="30/minute")
async def run_experimental_simulation(
    request: Request,
    body: ExperimentalSimRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Run a high-fidelity advanced chemical simulation synchronously.
    """
    solver = ExperimentalBiomineralizationSolver(
        co2_vol_pct=body.co2_vol_pct,
        so2_mg_per_nm3=body.so2_mg_per_nm3,
        nox_inlet_ppm=body.nox_inlet_ppm,
        ca_concentration_mg_l=body.ca_concentration_mg_l,
        calcium_source_g_per_l=body.calcium_source_g_per_l,
        crosslinking_density=body.crosslinking_density,
        mg_substitution_ratio=body.mg_substitution_ratio
    )
    res = solver.run()
    return res
