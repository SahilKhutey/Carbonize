"""
Celery job submission DoS prevention tests.
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


class TestCeleryDoSProtection:
    """Critical: prevent Celery queue flooding."""
    
    @pytest.mark.anyio
    async def test_20_burst_simulations_capped(
        self, client, authenticated_users, burst_login_tokens
    ):
        """
        DoD: 20 rapid simulation submissions from same user should
        result in at most 10 successes (10/minute limit).
        """
        user, org, plant_id = authenticated_users[0]
        token = burst_login_tokens[0]
        
        sim_payload = {
            "plant_profile_id": str(plant_id),
            "press_force_bar": 200.0,
            "enzyme_concentration_mg_l": 12.0,
            "chitosan_wt_pct": 3.0,
            "reactor_temperature_c": 40.0,
        }
        
        results = []
        start = time.perf_counter()
        
        for i in range(20):
            response = await client.post(
                "/api/simulations",
                json=sim_payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            results.append(response.status_code)
            
        elapsed = time.perf_counter() - start
        
        # Count outcomes
        status_counts = Counter(results)
        successes = status_counts.get(202, 0)
        rate_limited = status_counts.get(429, 0)
        
        assert successes <= 10, \
            f"Expected at most 10 successes, got {successes}. Status counts: {status_counts}"
            
        assert rate_limited >= 8, \
            f"Expected ≥8 rate-limited (429), got {rate_limited}"
            
        assert elapsed < 10, f"20 requests took {elapsed:.1f}s (too slow)"

    @pytest.mark.anyio
    async def test_50_rapid_simulations_only_10_dispatched(
        self, client, authenticated_users, burst_login_tokens
    ):
        """
        DoD: 50 concurrent rapid requests should result in at most 10 accepted.
        """
        user, org, plant_id = authenticated_users[0]
        token = burst_login_tokens[0]
        
        sim_payload = {
            "plant_profile_id": str(plant_id),
            "press_force_bar": 200.0,
            "enzyme_concentration_mg_l": 12.0,
            "chitosan_wt_pct": 3.0,
            "reactor_temperature_c": 40.0,
        }
        
        results = await asyncio.gather(*[
            client.post(
                "/api/simulations",
                json=sim_payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            for _ in range(50)
        ])
        
        statuses = [r.status_code for r in results]
        status_counts = Counter(statuses)
        
        successes = status_counts.get(202, 0)
        rate_limited = status_counts.get(429, 0)
        
        assert successes <= 10, \
            f"CELERY DoS VULNERABILITY: {successes} jobs accepted in burst! Expected ≤10."
            
        assert rate_limited >= 35, \
            f"Expected ≥35 rate-limited, got {rate_limited}"


class TestRequestSizeLimit:
    """Test that large request bodies are rejected."""
    
    @pytest.mark.anyio
    async def test_oversized_login_rejected(
        self, client
    ):
        """Huge login payload (>100KB) should be rejected with 413."""
        # Create a ~120KB payload
        huge_payload = {
            "email": "user@example.com",
            "password": "TestP@ssw0rd!23",
            "_huge_field": "X" * 120_000,
        }
        
        response = await client.post(
            "/api/auth/login",
            json=huge_payload,
        )
        
        assert response.status_code == 413

    @pytest.mark.anyio
    async def test_oversized_simulation_rejected(
        self, client, authenticated_users, burst_login_tokens
    ):
        """Huge simulation payload (>5MB) should be rejected with 413."""
        user, org, plant_id = authenticated_users[0]
        token = burst_login_tokens[0]
        
        huge_payload = {
            "plant_profile_id": str(plant_id),
            "press_force_bar": 200.0,
            "enzyme_concentration_mg_l": 12.0,
            "chitosan_wt_pct": 3.0,
            "reactor_temperature_c": 40.0,
            "_huge": "Y" * (6 * 1024 * 1024),
        }
        
        response = await client.post(
            "/api/simulations",
            json=huge_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 413
