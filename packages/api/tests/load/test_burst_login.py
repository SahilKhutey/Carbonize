"""
Burst load tests: ensure rate limits hold under burst traffic.
"""

import pytest
import time
from collections import Counter
from cbms_api.middleware.rate_limiting import limiter


@pytest.fixture(autouse=True)
def clear_limiter():
    """Clear rate limit storage between tests."""
    limiter._limiter.storage.reset()


class TestBurstLoginRateLimit:
    """Burst login attempts should be rate-limited."""
    
    @pytest.mark.anyio
    async def test_50_burst_logins_only_5_succeed(
        self, client, authenticated_users
    ):
        """
        DoD: 50 rapid login attempts from same IP should result
        in at most 5 successes (5/minute limit).
        """
        user, org, _ = authenticated_users[0]
        results = []
        start = time.perf_counter()
        
        for i in range(50):
            response = await client.post(
                "/api/auth/login",
                json={"email": user.email, "password": "LoadTest123!"},
            )
            results.append(response.status_code)
        
        elapsed = time.perf_counter() - start
        
        # Count outcomes
        status_counts = Counter(results)
        successes = status_counts.get(200, 0)
        rate_limited = status_counts.get(429, 0)
        
        # At most 5 successes (the limit)
        assert successes <= 5, \
            f"Expected at most 5 successes, got {successes}. Status counts: {status_counts}"
        
        # Many should be rate-limited
        assert rate_limited >= 40, \
            f"Expected ≥40 rate-limited (429), got {rate_limited}"
        
        # 50 attempts in reasonable time
        assert elapsed < 10, f"50 requests took {elapsed:.1f}s (too slow)"


class TestBurstLoginDifferentIPs:
    """Burst from different IPs should each get their own quota."""
    
    @pytest.mark.anyio
    async def test_different_ips_independent_quotas(
        self, client, authenticated_users
    ):
        """
        10 different IPs making 1 login each = 10 successful
        (each IP has its own 5/minute quota).
        """
        user, org, _ = authenticated_users[0]
        results = []
        
        for i in range(10):
            response = await client.post(
                "/api/auth/login",
                json={"email": user.email, "password": "LoadTest123!"},
                headers={"X-Forwarded-For": f"192.168.1.{i}"},
            )
            results.append(response.status_code)
            
        status_counts = Counter(results)
        successes = status_counts.get(200, 0)
        
        # 10 different IPs = 10 successes
        assert successes == 10, f"Expected 10 successes, got {successes}"
