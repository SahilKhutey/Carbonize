"""
Attempts to bypass tenant filtering via API query parameters or token manipulation.
"""

import pytest


class TestQueryParameterBypass:
    """Try to bypass tenant filter via various query parameters."""
    
    @pytest.mark.anyio
    async def test_org_id_query_param_ignored(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to set org_id in query params to override."""
        _, _, ids_b = tenant_b
        
        response = await client.get(
            f"/api/plants?org_id={ids_b['plant']}",
            headers=auth_a,
        )
        assert response.status_code == 200
        plants = response.json()
        ids = [p["id"] for p in plants]
        assert str(ids_b["plant"]) not in ids
    
    @pytest.mark.anyio
    async def test_filter_by_other_org_id(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to filter by B's org_id explicitly."""
        org_b, _, ids_b = tenant_b
        response = await client.get(
            f"/api/plants?filter_org_id={org_b.id}",
            headers=auth_a,
        )
        if response.status_code == 200:
            plants = response.json()
            ids = [p["id"] for p in plants]
            assert str(ids_b["plant"]) not in ids
    
    @pytest.mark.anyio
    async def test_include_other_tenant(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to include B's data via filter."""
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/plants?include_tenant_b=true",
            headers=auth_a,
        )
        assert response.status_code == 200
        plants = response.json()
        ids = [p["id"] for p in plants]
        assert str(ids_b["plant"]) not in ids
    
    @pytest.mark.anyio
    async def test_header_based_tenant_override(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to override tenant via custom header."""
        org_b, _, ids_b = tenant_b
        response = await client.get(
            "/api/plants",
            headers={
                **auth_a,
                "X-Tenant-Id": str(org_b.id),
            },
        )
        assert response.status_code == 200
        plants = response.json()
        ids = [p["id"] for p in plants]
        assert str(ids_b["plant"]) not in ids, \
            "X-Tenant-Id header allowed tenant override!"


class TestTokenManipulation:
    """Try to manipulate JWT to access other tenants."""
    
    @pytest.mark.anyio
    async def test_modified_jwt_claims_rejected(
        self, client, tenant_a, tenant_b
    ):
        """Try to modify org_id in JWT payload."""
        import base64
        import json
        from cbms_api.auth.jwt_service import jwt_service
        
        org_a, user_a, _ = tenant_a
        token_a = jwt_service.create_access_token(
            user_id=user_a.id,
            org_id=org_a.id,
            roles=user_a.roles,
            email=user_a.email,
            mfa_verified=True,
        )
        
        # Modify token claims
        parts = token_a.split(".")
        payload_part = parts[1]
        padding = 4 - len(payload_part) % 4
        payload_part += "=" * padding
        decoded = base64.urlsafe_b64decode(payload_part)
        claims = json.loads(decoded)
        
        # Modify org_id to B's organization ID
        org_b, _, _ = tenant_b
        claims["org_id"] = str(org_b.id)
        
        # Re-encode payload without generating a valid signature
        new_payload = base64.urlsafe_b64encode(
            json.dumps(claims).encode()
        ).rstrip(b"=").decode()
        tampered_token = f"{parts[0]}.{new_payload}.{parts[2]}"
        
        # Access plants with the tampered token
        response = await client.get(
            "/api/plants",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )
        assert response.status_code == 401
