"""
Admin endpoints tenant isolation tests.
"""

import pytest


@pytest.mark.anyio
async def test_admin_endpoint_isolation_placeholder(client, auth_a):
    # Tenant A attempts to access admin endpoints
    response = await client.get("/api/admin/users", headers=auth_a)
    assert response.status_code in [403, 404]
