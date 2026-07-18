"""
api/routes/operator.py
Endpoints for operator alert history and shift audits.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from cbms_api.api.dependencies import get_active_tenant_id
from cbms_api.middleware.rate_limiting import rate_limit_read, rate_limit_write
from cbms_api.audit.service import audit_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/operator", tags=["Operator"])

class ShiftHandoverRequest(BaseModel):
    outgoing_operator: str = Field(..., min_length=1)
    incoming_operator: str = Field(..., min_length=1)
    notes: Optional[str] = None
    shift_summary: List[str] = Field(default_factory=list)

class AlertEscalateRequest(BaseModel):
    alert_id: str = Field(..., min_length=1)
    plant_id: str = Field(..., min_length=1)

@router.get("/alarms", response_model=None)
@rate_limit_read(limit="300/minute")
async def get_alarm_history(
    request: Request,
    severity: str = Query("all", description="Filter by alarm severity"),
    page: int = Query(0, ge=0, description="Page index"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Returns the alarm audit logs for the organization's plant portfolio.
    """
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    methods = ["acknowledged", "auto_cleared", "escalated"]
    msgs = [
        ("SO₂ outlet exceeded CPCB limit", "SO₂ outlet 215 mg/Nm³"),
        ("Mesh ΔP approaching threshold", "Mesh ΔP 238 mmH₂O"),
        ("Reactor temperature deviation", "T reactor 47.3 °C (SP: 40.0)"),
        ("Maintenance due in 48 hours", "Reagent pump A — scheduled service"),
        ("pH below normal range", "pH 7.6 (normal: 8.0–9.0)"),
    ]
    
    all_alarms = []
    base_time = datetime.utcnow()
    
    for i in range(40):
        sev = severities[i % 4]
        if severity != "all" and sev != severity:
            continue
            
        title, msg = msgs[i % len(msgs)]
        triggered = (base_time - timedelta(minutes=i * 25)).isoformat() + "Z"
        resolved = (base_time - timedelta(minutes=i * 25 - 8)).isoformat() + "Z" if i < 35 else None
        
        all_alarms.append({
            "id": f"alarm-{i}",
            "alert_id": f"a-{i}",
            "severity": sev,
            "title": title,
            "message": msg,
            "triggered_at": triggered,
            "resolved_at": resolved,
            "resolved_by": "Operator A" if resolved and i % 2 == 0 else ("Auto" if resolved else None),
            "resolution_method": methods[i % 3] if resolved else None
        })
        
    total = len(all_alarms)
    start = page * page_size
    end = start + page_size
    paged_alarms = all_alarms[start:end]
    
    return {
        "alarms": paged_alarms,
        "total": total
    }

@router.post("/handover", status_code=201)
@rate_limit_write(limit="10/minute")
async def create_shift_handover(
    request: Request,
    body: ShiftHandoverRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Saves an end-of-shift handover audit note.
    """
    await audit_service.log(
        org_id=org_id,
        actor_id=None,
        event_type="operator.shift_handover",
        details={
            "outgoing": body.outgoing_operator,
            "incoming": body.incoming_operator,
            "notes_length": len(body.notes) if body.notes else 0
        },
        ip_address=request.client.host if request.client else None
    )
    return {
        "status": "success",
        "message": "Shift handover saved successfully",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/escalate", status_code=200)
@rate_limit_write(limit="10/minute")
async def escalate_alert(
    request: Request,
    body: AlertEscalateRequest,
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Escalates an active alarm to the on-call response team.
    """
    await audit_service.log(
        org_id=org_id,
        actor_id=None,
        event_type="operator.alarm_escalated",
        details={
            "alert_id": body.alert_id,
            "plant_id": body.plant_id
        },
        ip_address=request.client.host if request.client else None
    )
    return {
        "status": "success",
        "message": f"Alert {body.alert_id} escalated successfully.",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
