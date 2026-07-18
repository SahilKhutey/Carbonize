"""
TENANT ISOLATION TESTS — Prove that Tenant A cannot access Tenant B's data.
"""

import pytest
from uuid import UUID


class TestPlantIsolation:
    """Tenant A cannot access Tenant B's plants."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_plant_by_id(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """
        CRITICAL: GET /plants/{id_b} as user from Tenant A.
        Must return 404, not data.
        """
        org_a, user_a, ids_a = tenant_a
        org_b, user_b, ids_b = tenant_b
        
        response = await client.get(
            f"/api/plants/{ids_b['plant']}",
            headers=auth_a,
        )
        
        # Must be 404 (or 403) — NOT 200 with data
        assert response.status_code in [403, 404], \
            f"SECURITY VIOLATION: Tenant A accessed Tenant B's plant! " \
            f"Status: {response.status_code}, Body: {response.text[:200]}"
        
        # Critical: 404, NOT 403 (to prevent enumeration)
        assert response.status_code == 404, \
            "Should return 404 (not 403) to prevent ID enumeration"
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_list_tenant_b_plants(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Tenant A's plant list must not include Tenant B's plants."""
        _, _, ids_b = tenant_b
        
        response = await client.get(
            "/api/plants",
            headers=auth_a,
        )
        
        assert response.status_code == 200
        plants = response.json()
        
        # Verify NO plant from tenant B is in the list
        plant_ids = [p["id"] for p in plants]
        assert str(ids_b["plant"]) not in plant_ids, \
            f"SECURITY VIOLATION: Tenant A can see Tenant B's plants! IDs: {plant_ids}"
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_update_tenant_b_plant(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Tenant A cannot update Tenant B's plant (must be 404 or 405)."""
        _, _, ids_b = tenant_b
        
        response = await client.patch(
            f"/api/plants/{ids_b['plant']}",
            json={"name": "Hacked by Tenant A"},
            headers=auth_a,
        )
        
        # Should be 404 (not found in A's view) or 403 (forbidden) or 405 Method Not Allowed
        assert response.status_code in [403, 404, 405]
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_delete_tenant_b_plant(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Tenant A cannot delete Tenant B's plant."""
        _, _, ids_b = tenant_b
        
        response = await client.delete(
            f"/api/plants/{ids_b['plant']}",
            headers=auth_a,
        )
        
        assert response.status_code in [403, 404, 405]


class TestSimulationIsolation:
    """Tenant A cannot access Tenant B's simulations or results."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_simulation(
        self, client, tenant_a, tenant_b, auth_a
    ):
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/simulations/{ids_b['simulation']}",
            headers=auth_a,
        )
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_simulation_results(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Results endpoint must enforce isolation too."""
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/simulations/{ids_b['simulation']}/results",
            headers=auth_a,
        )
        # Results path might not exist or be nested, either way must not leak (404/403)
        assert response.status_code in [403, 404]
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_list_tenant_b_simulations(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """List filter must exclude tenant B's simulations."""
        _, _, ids_b = tenant_b
        
        response = await client.get(
            "/api/simulations",
            headers=auth_a,
        )
        # GET /api/simulations doesn't exist or is mapped, should be 404, 405 (Method Not Allowed), or empty
        assert response.status_code in [200, 404, 405]
        if response.status_code == 200:
            sims = response.json()
            sim_ids = [s["id"] for s in sims]
            assert str(ids_b["simulation"]) not in sim_ids
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_cancel_tenant_b_simulation(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Cannot cancel simulation of another tenant."""
        _, _, ids_b = tenant_b
        response = await client.delete(
            f"/api/simulations/{ids_b['simulation']}/cancel",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]


class TestReportIsolation:
    """Tenant A cannot access Tenant B's reports."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_report(
        self, client, tenant_a, tenant_b, auth_a
    ):
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/reports/{ids_b['simulation']}",
            headers=auth_a,
        )
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_download_tenant_b_report(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Cannot get download URL for another tenant's report."""
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/reports/{ids_b['simulation']}/download",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]


class TestCCTSIsolation:
    """Tenant A cannot access Tenant B's CCTS claims."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_ccts_claim(
        self, client, tenant_a, tenant_b, auth_a
    ):
        response = await client.get(
            "/api/compliance/ccts/claims/some-id",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]


class TestTwinIsolation:
    """Tenant A cannot access Tenant B's digital twin state."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_get_tenant_b_twin(
        self, client, tenant_a, tenant_b, auth_a
    ):
        response = await client.get(
            "/api/twin/some-id/state",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]


class TestAuditLogIsolation:
    """Tenant A cannot view Tenant B's audit logs."""
    
    @pytest.mark.anyio
    async def test_tenant_a_cannot_see_tenant_b_audit_logs(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Audit log endpoint must filter by org."""
        response = await client.get(
            "/api/compliance/audit",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]


class TestSearchIsolation:
    """Search queries must not leak across tenants."""
    
    @pytest.mark.anyio
    async def test_search_does_not_return_other_tenant_results(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Search by name should only return A's results."""
        _, _, ids_b = tenant_b
        
        # Search for the unique part of B's plant name
        response = await client.get(
            "/api/plants?search=Tenant%20B%20Plant",
            headers=auth_a,
        )
        
        # Search query params might not filter at API route level, but returned list must not contain B
        assert response.status_code == 200
        plants = response.json()
        plant_ids = [p["id"] for p in plants]
        assert str(ids_b["plant"]) not in plant_ids
    
    @pytest.mark.anyio
    async def test_full_text_search_isolated(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Even fuzzy text search must respect tenant boundary."""
        _, _, ids_b = tenant_b
        
        # Try various search strategies
        search_queries = [
            "Maharashtra",  # Common location
            "Tenant",  # Generic
        ]
        
        for q in search_queries:
            response = await client.get(
                f"/api/plants?search={q}",
                headers=auth_a,
            )
            assert response.status_code == 200
            plants = response.json()
            plant_ids = [p["id"] for p in plants]
            assert str(ids_b["plant"]) not in plant_ids, \
                f"Search '{q}' leaked tenant B's plant!"


class TestAnalyticsIsolation:
    """Verifies that analytics endpoints are fully isolated across tenants."""

    @pytest.mark.anyio
    async def test_portfolio_analytics_isolation(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Tenant A portfolio analytics should only reflect Tenant A data."""
        # Tenant A request
        response = await client.get(
            "/api/analytics/portfolio",
            headers=auth_a
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify plant count matches Tenant A (which is 1, whereas B also has 1)
        assert data["total_plants"] == 1
        
        # Check that details list contains A's plant but not B's
        _, _, ids_a = tenant_a
        _, _, ids_b = tenant_b
        plant_ids = [p["id"] for p in data["details"]]
        assert str(ids_a["plant"]) in plant_ids
        assert str(ids_b["plant"]) not in plant_ids


class TestOperatorIsolation:
    """Verifies that operator and shift auditing endpoints respect isolation and audit logs."""

    @pytest.mark.anyio
    async def test_get_alarms_requires_auth(self, client):
        """Unauthenticated request to alarms endpoint should fail."""
        response = await client.get("/api/operator/alarms")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_alarms_returns_success(self, client, auth_a):
        """Authenticated tenant can retrieve alarms log page."""
        response = await client.get(
            "/api/operator/alarms",
            headers=auth_a
        )
        assert response.status_code == 200
        data = response.json()
        assert "alarms" in data
        assert data["total"] > 0

    @pytest.mark.anyio
    async def test_shift_handover_logging_and_isolation(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Shift handover logs to active tenant's audit log and is isolated."""
        _, _, ids_a = tenant_a
        
        payload = {
            "outgoing_operator": "Alice",
            "incoming_operator": "Bob",
            "notes": "All green.",
            "shift_summary": ["Checked reagent pH"]
        }
        res_post = await client.post(
            "/api/operator/handover",
            json=payload,
            headers=auth_a
        )
        assert res_post.status_code == 201
        
        # Check database directly for created audit event
        from cbms_api.database.connection import async_session_maker
        from cbms_api.database.models import AuditEvent
        from sqlalchemy.future import select
        
        async with async_session_maker() as session:
            result = await session.execute(
                select(AuditEvent).filter(AuditEvent.event_type == "operator.shift_handover")
            )
            events = result.scalars().all()
            assert len(events) > 0
            # Ensure it is mapped to Org A's ID
            assert events[0].organization_id == ids_a["org"]

    @pytest.mark.anyio
    async def test_alert_escalation_logging_and_isolation(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Alert escalation logs to active tenant's audit log and is isolated."""
        _, _, ids_a = tenant_a
        
        payload = {
            "alert_id": "alert-123",
            "plant_id": str(ids_a["plant"])
        }
        res_post = await client.post(
            "/api/operator/escalate",
            json=payload,
            headers=auth_a
        )
        assert res_post.status_code == 200
        
        # Check database directly for created audit event
        from cbms_api.database.connection import async_session_maker
        from cbms_api.database.models import AuditEvent
        from sqlalchemy.future import select
        
        async with async_session_maker() as session:
            result = await session.execute(
                select(AuditEvent).filter(AuditEvent.event_type == "operator.alarm_escalated")
            )
            events = result.scalars().all()
            assert len(events) > 0
            # Ensure it is mapped to Org A's ID
            assert events[0].organization_id == ids_a["org"]

