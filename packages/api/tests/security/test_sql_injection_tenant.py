"""
SQL injection attempts targeting tenant isolation.
"""

import pytest


class TestSQLInjectionTenantBoundary:
    """Try SQL injection to bypass tenant filtering."""
    
    @pytest.mark.anyio
    async def test_sql_injection_in_search_param(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """SQL injection in search parameter."""
        _, _, ids_b = tenant_b
        
        # Classic SQL injection attempts
        payloads = [
            "'; DROP TABLE plant_profiles; --",
            "' OR '1'='1",
            "'; SELECT * FROM plant_profiles; --",
            "1' UNION SELECT * FROM plant_profiles WHERE organization_id != '" + str(tenant_a[0].id) + "'--",
            "' OR organization_id IS NULL --",
            "1 OR 1=1",
        ]
        
        for payload in payloads:
            response = await client.get(
                f"/api/plants?search={payload}",
                headers=auth_a,
            )
            # Either 200 (safe, escaped) or 400/422 (validation)
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                # If 200, response must not include B's data
                plants = response.json()
                ids = [p["id"] for p in plants]
                assert str(ids_b["plant"]) not in ids, \
                    f"SQL injection '{payload}' leaked data!"
    
    @pytest.mark.anyio
    async def test_sql_injection_in_path_param(
        self, client, auth_a
    ):
        """SQL injection in path parameters (UUID fields)."""
        payloads = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "1 UNION SELECT * FROM plant_profiles--",
        ]
        
        for payload in payloads:
            response = await client.get(
                f"/api/plants/{payload}",
                headers=auth_a,
            )
            # UUID validation should reject
            assert response.status_code in [400, 404, 422]
    
    @pytest.mark.anyio
    async def test_sql_injection_in_body(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """SQL injection in JSON body fields."""
        _, _, ids_b = tenant_b
        
        # Try to inject into name field
        response = await client.post(
            "/api/plants",
            json={
                "name": "'; DROP TABLE plant_profiles; --",
                "location": "A-City",
                "boiler_type": "pulverized",
                "exhaust_flow_rate": 10000,
                "baseline_temperature": 150,
                "co2_concentration": 14,
                "so2_concentration": 1200,
                "fly_ash_load": 45,
                "nox_concentration": 500,
                "water_cost_per_kl": 10.0,
                "electricity_cost_per_kwh": 5.0,
                "chitosan_cost_per_kg": 300.0,
                "calcium_source_type": "Ca(OH)2",
                "calcium_cost_per_ton": 80.0,
                "local_brick_market_value": 15.0,
                "ccts_credit_price": 20.0,
            },
            headers=auth_a,
        )
        # Either succeeds (with safe string) or validation error
        assert response.status_code in [201, 400, 422]
        
        # Verify B's plant still exists and is not visible to A
        response = await client.get(
            f"/api/plants/{ids_b['plant']}",
            headers=auth_a,
        )
        assert response.status_code == 404


class TestNoSQLInjection:
    """NoSQL injection attempts."""
    
    @pytest.mark.anyio
    async def test_nosql_injection_in_query(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """NoSQL-style operator injection."""
        _, _, ids_b = tenant_b
        
        payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$where": "1==1"}',
        ]
        
        for payload in payloads:
            response = await client.get(
                f"/api/plants?search={payload}",
                headers=auth_a,
            )
            # Should not bypass RLS
            if response.status_code == 200:
                plants = response.json()
                ids = [p["id"] for p in plants]
                assert str(ids_b["plant"]) not in ids
