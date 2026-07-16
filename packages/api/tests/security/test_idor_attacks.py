"""
IDOR (Insecure Direct Object Reference) attack tests.
"""

import pytest
import uuid


class TestIDORAttacks:
    """Attempt IDOR attacks on every resource type."""
    
    @pytest.mark.anyio
    async def test_idor_with_uuid_v1(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to access with B's UUID (v1)."""
        _, _, ids_b = tenant_b
        response = await client.get(
            f"/api/plants/{ids_b['plant']}",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]
    
    @pytest.mark.anyio
    async def test_idor_with_uuid_v4(
        self, client, auth_a
    ):
        """Try a random UUID."""
        response = await client.get(
            f"/api/plants/{uuid.uuid4()}",
            headers=auth_a,
        )
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_idor_with_zero_uuid(
        self, client, auth_a
    ):
        """Try the all-zeros UUID."""
        response = await client.get(
            "/api/plants/00000000-0000-0000-0000-000000000000",
            headers=auth_a,
        )
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_idor_path_traversal(
        self, client, tenant_b, auth_a
    ):
        """Try path traversal in URL."""
        _, _, ids_b = tenant_b
        malicious_ids = [
            f"{ids_b['plant']}/../",
            f"{ids_b['plant']}%2F..%2F",
            f"{ids_b['plant']}#fragment",
            f"../{ids_b['plant']}",
        ]
        
        for malicious in malicious_ids:
            response = await client.get(
                f"/api/plants/{malicious}",
                headers=auth_a,
            )
            # Should be 307, 400, 404 or 422 (invalid UUID, resource not found or redirected), NOT 200
            assert response.status_code in [307, 400, 404, 422], \
                f"Path traversal '{malicious}' returned {response.status_code}"
    
    @pytest.mark.anyio
    async def test_idor_with_tenant_b_user_id(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to access tenant B's user as tenant A."""
        _, user_b, _ = tenant_b
        response = await client.get(
            f"/api/admin/users/{user_b.id}",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]
    
    @pytest.mark.anyio
    async def test_idor_with_tenant_b_org_id(
        self, client, tenant_a, tenant_b, auth_a
    ):
        """Try to read tenant B's org info."""
        org_b, _, _ = tenant_b
        response = await client.get(
            f"/api/organizations/{org_b.id}",
            headers=auth_a,
        )
        assert response.status_code in [403, 404]
