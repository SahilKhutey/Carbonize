"""
Integration tests for the /analytics route module.

Tests:
  - GET /analytics/portfolio — auth guard, response shape, tenant isolation,
    total_plants count, details list, KPI structure
"""

import pytest


class TestPortfolioAnalytics:
    """Verify the portfolio analytics endpoint shape and tenant isolation."""

    @pytest.mark.anyio
    async def test_portfolio_requires_auth(self, client):
        """Unauthenticated request is rejected."""
        res = await client.get("/api/analytics/portfolio")
        assert res.status_code == 401

    @pytest.mark.anyio
    async def test_portfolio_returns_200(self, client, auth_a):
        """Authenticated request returns 200."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200

    @pytest.mark.anyio
    async def test_portfolio_top_level_keys(self, client, auth_a):
        """Response contains required top-level keys consumed by tests and frontend."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        # Keys required by tenant-isolation security tests
        assert "total_plants" in data, "Missing required key: total_plants"
        assert "details" in data, "Missing required key: details"
        # Keys consumed by the frontend hook
        assert "summary" in data
        assert "plants" in data
        assert "insights" in data

    @pytest.mark.anyio
    async def test_portfolio_total_plants_count(self, client, tenant_a, auth_a):
        """total_plants reflects the actual number of plants for this tenant."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        # tenant_a fixture creates exactly 1 plant
        assert data["total_plants"] == 1

    @pytest.mark.anyio
    async def test_portfolio_details_contains_tenant_plant(self, client, tenant_a, auth_a):
        """details list contains the tenant's plant id."""
        _, _, ids_a = tenant_a
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        plant_ids = [p["id"] for p in data["details"]]
        assert str(ids_a["plant"]) in plant_ids

    @pytest.mark.anyio
    async def test_portfolio_tenant_isolation(self, client, tenant_a, tenant_b, auth_a):
        """Tenant A's portfolio must not expose Tenant B's plant."""
        _, _, ids_b = tenant_b
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        data = res.json()
        plant_ids = [p["id"] for p in data["details"]]
        assert str(ids_b["plant"]) not in plant_ids, \
            "SECURITY: Tenant A can see Tenant B's plant in analytics!"

    @pytest.mark.anyio
    async def test_portfolio_summary_kpis_present(self, client, auth_a):
        """Summary must contain a kpis list and lastUpdated timestamp."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        summary = res.json()["summary"]
        assert "kpis" in summary
        assert isinstance(summary["kpis"], list)
        assert len(summary["kpis"]) > 0
        assert "lastUpdated" in summary

    @pytest.mark.anyio
    async def test_portfolio_kpi_shape(self, client, auth_a):
        """Each KPI entry must have id, label, value, trend fields."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        for kpi in res.json()["summary"]["kpis"]:
            assert "id" in kpi
            assert "label" in kpi
            assert "value" in kpi
            assert "trend" in kpi

    @pytest.mark.anyio
    async def test_portfolio_plant_rows_shape(self, client, auth_a):
        """Each plant row must have id, name, status, co2CapturePct fields."""
        res = await client.get("/api/analytics/portfolio", headers=auth_a)
        assert res.status_code == 200
        for plant in res.json()["plants"]:
            assert "id" in plant
            assert "name" in plant
            assert "status" in plant
            assert "co2CapturePct" in plant

    @pytest.mark.anyio
    async def test_portfolio_period_filter_accepted(self, client, auth_a):
        """Period query param is accepted without error."""
        res = await client.get("/api/analytics/portfolio?period=30d", headers=auth_a)
        assert res.status_code == 200
