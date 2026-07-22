"""
api/routes/operator.py
Endpoints for operator alert history, shift handover, and alarm escalation.

Changes v2:
  - datetime.utcnow() → datetime.now(UTC)  (Python 3.12 deprecation fix)
  - /escalate now fires real webhook/email/PagerDuty notifications via
    cbms_api.services.notification.notification_service
  - /escalate accepts optional severity, plant_name, and message fields
  - /handover returns timezone-aware ISO timestamp
"""

from __future__ import annotations

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta, UTC

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Query
from pydantic import BaseModel, Field

from cbms_api.api.dependencies import get_active_tenant_id
from cbms_api.auth.rbac import get_current_active_user, AuthUser
from cbms_api.middleware.rate_limiting import rate_limit_read, rate_limit_write
from cbms_api.audit.service import audit_service
from cbms_api.services.notification import notification_service

router = APIRouter(prefix="/operator", tags=["Operator"])


class ShiftHandoverRequest(BaseModel):
    outgoing_operator: str = Field(..., min_length=1)
    incoming_operator: str = Field(..., min_length=1)
    notes: Optional[str] = None
    shift_summary: List[str] = Field(default_factory=list)


class AlertEscalateRequest(BaseModel):
    alert_id:   str = Field(..., min_length=1)
    plant_id:   str = Field(..., min_length=1)
    plant_name: str = Field(default="")
    severity:   str = Field(default="HIGH")
    message:    str = Field(default="")


@router.get("/alarms", response_model=None)
@rate_limit_read(limit="300/minute")
async def get_alarm_history(
    request: Request,
    severity: str = Query("all", description="Filter by alarm severity"),
    page: int = Query(0, ge=0, description="Page index"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    org_id: UUID = Depends(get_active_tenant_id),
):
    """
    Returns the alarm audit logs for the organisation's plant portfolio.
    NOTE: In production these rows are read from the sensor_readings / audit_events
    tables.  This implementation synthesises plausible rows for UI development
    until the real-time data pipeline is deployed.
    """
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    methods    = ["acknowledged", "auto_cleared", "escalated"]
    msgs = [
        ("SO₂ outlet exceeded CPCB limit",   "SO₂ outlet 215 mg/Nm³"),
        ("Mesh ΔP approaching threshold",     "Mesh ΔP 238 mmH₂O"),
        ("Reactor temperature deviation",     "T reactor 47.3 °C (SP: 40.0)"),
        ("Maintenance due in 48 hours",       "Reagent pump A — scheduled service"),
        ("pH below normal range",             "pH 7.6 (normal: 8.0–9.0)"),
    ]

    all_alarms = []
    base_time = datetime.now(UTC)

    for i in range(40):
        sev = severities[i % 4]
        if severity != "all" and sev != severity:
            continue

        title, msg = msgs[i % len(msgs)]
        triggered  = (base_time - timedelta(minutes=i * 25)).isoformat()
        resolved   = (
            (base_time - timedelta(minutes=i * 25 - 8)).isoformat()
            if i < 35 else None
        )

        all_alarms.append({
            "id":                f"alarm-{i}",
            "alert_id":          f"a-{i}",
            "severity":          sev,
            "title":             title,
            "message":           msg,
            "triggered_at":      triggered,
            "resolved_at":       resolved,
            "resolved_by":       (
                "Operator A" if resolved and i % 2 == 0
                else ("Auto" if resolved else None)
            ),
            "resolution_method": methods[i % 3] if resolved else None,
        })

    total        = len(all_alarms)
    start        = page * page_size
    paged_alarms = all_alarms[start : start + page_size]

    return {"alarms": paged_alarms, "total": total}


@router.post("/handover", status_code=201)
@rate_limit_write(limit="10/minute")
async def create_shift_handover(
    request: Request,
    body: ShiftHandoverRequest,
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Saves an end-of-shift handover audit record."""
    await audit_service.log(
        org_id=current_user.org_id,
        actor_id=str(current_user.user_id),
        event_type="operator.shift_handover",
        ip_address=request.client.host if request.client else None,
    )
    return {
        "status":    "success",
        "message":   "Shift handover saved successfully",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.post("/escalate", status_code=200)
@rate_limit_write(limit="10/minute")
async def escalate_alert(
    request: Request,
    body: AlertEscalateRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_active_user),
):
    """
    Escalates an active alarm to the on-call response team.

    Fires real notifications (webhook / email / PagerDuty) through all
    channels configured via environment variables.  Notification delivery
    runs in a background task so the API response is not blocked.
    """
    now = datetime.now(UTC)

    await audit_service.log(
        org_id=current_user.org_id,
        actor_id=str(current_user.user_id),
        event_type="operator.alarm_escalated",
        ip_address=request.client.host if request.client else None,
    )

    # Fire notifications in background — does not block the HTTP response
    background_tasks.add_task(
        notification_service.notify_escalation,
        alert_id=body.alert_id,
        plant_id=body.plant_id,
        plant_name=body.plant_name,
        severity=body.severity,
        title=f"[{body.severity}] Alarm escalated at {body.plant_name or body.plant_id}",
        message=body.message,
        actor=str(current_user.user_id),
        escalated_at=now,
    )

    return {
        "status":    "success",
        "message":   f"Alert {body.alert_id} escalated. Notifications dispatched.",
        "timestamp": now.isoformat(),
    }
