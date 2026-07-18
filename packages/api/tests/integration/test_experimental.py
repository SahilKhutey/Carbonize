import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from cbms_api.api.main import app
from cbms_api.api.dependencies import get_active_tenant_id

# Override tenant dependency to return a dummy UUID so we bypass auth database checks
dummy_org_id = uuid4()
app.dependency_overrides[get_active_tenant_id] = lambda: dummy_org_id


@pytest.mark.anyio
async def test_experimental_simulate_route_success():
    """Verify that posting to /api/experimental/simulate runs successfully."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "co2_vol_pct": 14.0,
            "so2_mg_per_nm3": 1200.0,
            "nox_inlet_ppm": 250.0,
            "ca_concentration_mg_l": 12.0,
            "calcium_source_g_per_l": 35.0,
            "crosslinking_density": 0.5,
            "mg_substitution_ratio": 0.3
        }
        
        response = await client.post("/api/experimental/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "efficiencies" in data
        assert data["efficiencies"]["NOx"] > 0.0
        assert data["block_strength_mpa"] > 0.0
        assert "sizing" in data
        assert data["sizing"]["vessel_diameter_m"] > 0.0
        assert data["sizing"]["adjusted_operating_hours"] <= 8760.0
