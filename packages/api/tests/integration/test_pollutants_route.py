"""
Integration tests for /api/pollutants database and impact assessment endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from cbms_api.api.main import app
from cbms_api.api.dependencies import get_active_tenant_id


@pytest.fixture(autouse=True)
def override_tenant():
    dummy_org_id = uuid4()
    app.dependency_overrides[get_active_tenant_id] = lambda: dummy_org_id
    yield
    app.dependency_overrides.pop(get_active_tenant_id, None)


@pytest.mark.anyio
async def test_get_pollutants_database_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/pollutants/database")
        assert res.status_code == 200
        data = res.json()
        assert "CO2" in data
        assert "SO2" in data
        assert data["SO2"]["cpcb_limit_mg_per_nm3"] == 200.0


@pytest.mark.anyio
async def test_assess_pollutant_impact_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "co2_vol_pct": 14.0,
            "so2_mg_per_nm3": 650.0,
            "nox_mg_per_nm3": 450.0,
            "fly_ash_g_per_nm3": 25.0,
            "exhaust_flow_nm3_hr": 10000.0
        }
        res = await ac.post("/api/pollutants/assess-impact", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["ph_drop_rate_per_min"] > 0.0
        assert data["ca_enzyme_inactivation_acceleration_factor"] > 1.0
        assert "recommended_control_actions" in data
