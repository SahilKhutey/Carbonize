"""
Integration tests for the /operator route module.

Tests:
  - GET /operator/alarms — pagination, severity filter, auth guard
  - POST /operator/handover — creates audit log with correct actor_id and org_id
  - POST /operator/escalate — creates audit log with correct actor_id and org_id

Fixture dependencies (inherited from security/conftest.py pattern via conftest chain):
  client, tenant_a, auth_a, setup_test_data
"""

import pytest
from uuid import uuid4


class TestOperatorAlarms:
    """Verify the alarm history endpoint."""

    @pytest.mark.anyio
    async def test_alarms_requires_auth(self, client):
        """Unauthenticated request is rejected."""
        res = await client.get("/api/operator/alarms")
        assert res.status_code == 401

    @pytest.mark.anyio
    async def test_alarms_returns_paginated_results(self, client, auth_a):
        """Authenticated request returns paginated alarm list."""
        res = await client.get("/api/operator/alarms?page=0&page_size=5", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        assert "alarms" in data
        assert "total" in data
        assert isinstance(data["alarms"], list)
        assert len(data["alarms"]) <= 5

    @pytest.mark.anyio
    async def test_alarms_severity_filter(self, client, auth_a):
        """Severity filter returns only matching alarms."""
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            res = await client.get(f"/api/operator/alarms?severity={sev}", headers=auth_a)
            assert res.status_code == 200
            data = res.json()
            for alarm in data["alarms"]:
                assert alarm["severity"] == sev

    @pytest.mark.anyio
    async def test_alarms_page_out_of_range_returns_empty(self, client, auth_a):
        """Requesting a page beyond the end returns an empty alarm list."""
        res = await client.get("/api/operator/alarms?page=9999&page_size=10", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        assert data["alarms"] == []


class TestShiftHandover:
    """Verify POST /operator/handover creates a valid audit record."""

    @pytest.mark.anyio
    async def test_handover_requires_auth(self, client):
        """Unauthenticated request is rejected."""
        res = await client.post(
            "/api/operator/handover",
            json={"outgoing_operator": "Alice", "incoming_operator": "Bob"},
        )
        assert res.status_code == 401

    @pytest.mark.anyio
    async def test_handover_success(self, client, auth_a):
        """Valid handover request returns 201 with success status."""
        payload = {
            "outgoing_operator": "Alice",
            "incoming_operator": "Bob",
            "notes": "All green. Reagent levels nominal.",
            "shift_summary": ["Checked pH", "Reagent top-up done"],
        }
        res = await client.post("/api/operator/handover", json=payload, headers=auth_a)
        assert res.status_code == 201
        body = res.json()
        assert body["status"] == "success"
        assert "timestamp" in body

    @pytest.mark.anyio
    async def test_handover_missing_fields_returns_422(self, client, auth_a):
        """Missing required field outgoing_operator triggers validation error."""
        res = await client.post(
            "/api/operator/handover",
            json={"incoming_operator": "Bob"},
            headers=auth_a,
        )
        assert res.status_code == 422

    @pytest.mark.anyio
    async def test_handover_creates_audit_event(self, client, tenant_a, auth_a):
        """Handover creates an AuditEvent with the correct org_id and event_type."""
        _, _, ids_a = tenant_a
        payload = {
            "outgoing_operator": "Charlie",
            "incoming_operator": "Diana",
        }
        res = await client.post("/api/operator/handover", json=payload, headers=auth_a)
        assert res.status_code == 201

        from cbms_api.database.connection import async_session_maker
        from cbms_api.database.models import AuditEvent
        from sqlalchemy.future import select

        async with async_session_maker() as session:
            result = await session.execute(
                select(AuditEvent)
                .filter(AuditEvent.event_type == "operator.shift_handover")
                .filter(AuditEvent.organization_id == ids_a["org"])
            )
            events = result.scalars().all()
        assert len(events) >= 1
        # actor_id must be a non-None UUID string (not the old 'None' sentinel)
        assert events[0].actor_id is not None
        assert events[0].actor_id != "None"


class TestAlertEscalation:
    """Verify POST /operator/escalate creates a valid audit record."""

    @pytest.mark.anyio
    async def test_escalate_requires_auth(self, client):
        """Unauthenticated request is rejected."""
        res = await client.post(
            "/api/operator/escalate",
            json={"alert_id": "a-1", "plant_id": str(uuid4())},
        )
        assert res.status_code == 401

    @pytest.mark.anyio
    async def test_escalate_success(self, client, tenant_a, auth_a):
        """Valid escalation request returns 200 with success status."""
        _, _, ids_a = tenant_a
        res = await client.post(
            "/api/operator/escalate",
            json={"alert_id": "alarm-42", "plant_id": str(ids_a["plant"])},
            headers=auth_a,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "success"
        assert "alarm-42" in body["message"]

    @pytest.mark.anyio
    async def test_escalate_missing_plant_id_returns_422(self, client, auth_a):
        """Missing plant_id triggers validation error."""
        res = await client.post(
            "/api/operator/escalate",
            json={"alert_id": "alarm-1"},
            headers=auth_a,
        )
        assert res.status_code == 422

    @pytest.mark.anyio
    async def test_escalate_creates_audit_event(self, client, tenant_a, auth_a):
        """Escalation creates an AuditEvent with correct org_id and non-null actor_id."""
        _, _, ids_a = tenant_a
        res = await client.post(
            "/api/operator/escalate",
            json={"alert_id": "alarm-99", "plant_id": str(ids_a["plant"])},
            headers=auth_a,
        )
        assert res.status_code == 200

        from cbms_api.database.connection import async_session_maker
        from cbms_api.database.models import AuditEvent
        from sqlalchemy.future import select

        async with async_session_maker() as session:
            result = await session.execute(
                select(AuditEvent)
                .filter(AuditEvent.event_type == "operator.alarm_escalated")
                .filter(AuditEvent.organization_id == ids_a["org"])
            )
            events = result.scalars().all()
        assert len(events) >= 1
        assert events[0].actor_id is not None
        assert events[0].actor_id != "None"
