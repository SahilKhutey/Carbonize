"""
Comprehensive load test: verify rate limits hold under sustained load.
"""

import pytest
import asyncio
import time
from collections import Counter
from cbms_api.middleware.rate_limiting import limiter


@pytest.fixture(autouse=True)
def clear_limiter():
    """Clear rate limit storage between tests."""
    limiter._limiter.storage.reset()


class TestSustainedLoad:
    """Rate limits under sustained load."""
    
    @pytest.mark.anyio
    async def test_sustained_load_profile(
        self, client, authenticated_users, burst_login_tokens
    ):
        """
        DoD: Rapid requests to read endpoint should not result in 5xx errors.
        """
        token = burst_login_tokens[0]
        results = []
        start = time.perf_counter()
        
        # Make 30 rapid GET calls to /api/plants
        for _ in range(30):
            response = await client.get(
                "/api/plants",
                headers={"Authorization": f"Bearer {token}"},
            )
            results.append(response.status_code)
            
        elapsed = time.perf_counter() - start
        status_counts = Counter(results)
        
        # No 5xx errors (server must handle load cleanly)
        server_errors = sum(v for k, v in status_counts.items() if 500 <= k < 600)
        assert server_errors == 0, f"Got server errors: {status_counts}"


class TestRateLimitIsolation:
    """Rate limits must be isolated per-user / per-IP."""
    
    @pytest.mark.anyio
    async def test_user_a_429_does_not_affect_user_b(
        self, client, authenticated_users
    ):
        """
        If User A is rate-limited on login, User B should still get through.
        """
        user_a, _, _ = authenticated_users[0]
        user_b, _, _ = authenticated_users[1]
        
        # User A makes 6 login attempts (limit is 5/minute)
        a_results = []
        for _ in range(6):
            response = await client.post(
                "/api/auth/login",
                json={"email": user_a.email, "password": "LoadTest123!"},
                headers={"X-Forwarded-For": "192.168.2.1"},
            )
            a_results.append(response.status_code)
            
        # Verify A got rate-limited
        assert 429 in a_results, f"User A should have been rate-limited: {a_results}"
        
        # User B makes a login attempt from a different IP
        response = await client.post(
            "/api/auth/login",
            json={"email": user_b.email, "password": "LoadTest123!"},
            headers={"X-Forwarded-For": "192.168.2.2"},
        )
        
        # User B should NOT get 429 (should get 200)
        assert response.status_code == 200, f"User B should get 200, got {response.status_code}"
