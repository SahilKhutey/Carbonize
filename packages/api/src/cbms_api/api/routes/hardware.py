"""
hardware.py
FastAPI router for Hardware Guidance & Reactor Sizing Specification Handoff.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

from cbms_sim.domain.hardware.spec_sheet import HardwareSpecSheetGenerator
from cbms_sim.domain.hardware.exporter import HardwareSpecMarkdownExporter
from cbms_api.middleware.rate_limiting import rate_limit_write
from cbms_api.api.dependencies import get_active_tenant_id

router = APIRouter(prefix="/hardware", tags=["Hardware Guidance"])


class HardwareSpecRequest(BaseModel):
    exhaust_flow_nm3_hr: float = Field(default=10000.0, ge=100.0, le=1000000.0)
    target_co2_capture_pct: float = Field(default=85.0, ge=10.0, le=99.9)
    residence_time_s: float = Field(default=27.0, ge=1.0, le=300.0)
    liquid_to_gas_ratio: float = Field(default=8.5, ge=0.5, le=50.0)
    chitosan_wt_pct: float = Field(default=3.0, ge=0.1, le=20.0)
    ca_lime_wt_pct: float = Field(default=3.5, ge=0.1, le=20.0)
    enzyme_dosage_mg_l: float = Field(default=12.0, ge=0.0, le=200.0)
    comparator_result: Optional[Dict[str, Any]] = None
    provenance_status: Optional[str] = "🟡 Literature-derived"


@router.post("/spec-sheet")
@rate_limit_write(limit="30/minute")
async def generate_hardware_spec_sheet(
    request: Request,
    body: HardwareSpecRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Generate a formal Hardware Sizing & Procurement Spec Sheet deliverable
    with Gated Engineering Safety Factors (+15% to +50%) and Unified Trust Score.
    """
    generator = HardwareSpecSheetGenerator()
    spec = generator.generate(
        exhaust_flow_nm3_hr=body.exhaust_flow_nm3_hr,
        target_co2_capture_pct=body.target_co2_capture_pct,
        residence_time_s=body.residence_time_s,
        liquid_to_gas_ratio=body.liquid_to_gas_ratio,
        chitosan_wt_pct=body.chitosan_wt_pct,
        ca_lime_wt_pct=body.ca_lime_wt_pct,
        comparator_result=body.comparator_result,
        provenance_status=body.provenance_status or "🟡 Literature-derived",
    )
    return spec


@router.post("/spec-sheet/export-markdown", response_class=PlainTextResponse)
@rate_limit_write(limit="30/minute")
async def export_hardware_spec_markdown(
    request: Request,
    body: HardwareSpecRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Export Hardware Sizing & Procurement Spec Sheet as printable Markdown text.
    """
    generator = HardwareSpecSheetGenerator()
    spec = generator.generate(
        exhaust_flow_nm3_hr=body.exhaust_flow_nm3_hr,
        target_co2_capture_pct=body.target_co2_capture_pct,
        residence_time_s=body.residence_time_s,
        liquid_to_gas_ratio=body.liquid_to_gas_ratio,
        chitosan_wt_pct=body.chitosan_wt_pct,
        ca_lime_wt_pct=body.ca_lime_wt_pct,
        enzyme_dosage_mg_l=body.enzyme_dosage_mg_l,
        comparator_result=body.comparator_result,
        provenance_status=body.provenance_status or "🟡 Literature-derived",
    )
    exporter = HardwareSpecMarkdownExporter()
    return exporter.export_to_markdown(spec)
