"""
Comprehensive rate limiting with SlowAPI.

Features:
- Per-user (when authenticated) and per-IP (when not) limiting
- Tier-based limits (AUTH, EXPENSIVE, WRITE, READ)
- Custom rate limit decorator for endpoint-specific limits
- Rate limit metrics for observability
"""

from typing import Callable, Optional
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from cbms_api.config import get_settings
from cbms_api.rate_limits import RATE_LIMITS, RateLimitTier


settings = get_settings()


# =============================================================================
# RATE LIMITER KEY FUNCTION
# =============================================================================

def get_rate_limit_key(request: Request) -> str:
    """
    Get the rate limit key for a request.
    
    Priority: authenticated user > IP address
    """
    # Check if user is authenticated (via auth middleware or dependency user attribute)
    user = getattr(request.state, "user", None)
    if user is not None:
        user_id = getattr(user, "id", None) or getattr(user, "user_id", None)
        if user_id:
            return f"user:{user_id}"
            
    # Check for X-Forwarded-For header first (trusted proxy)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Get the first IP in the list
        ip = forwarded.split(",")[0].strip()
        return f"ip:{ip}"
        
    return f"ip:{get_remote_address(request)}"


# Determine storage backend: use memory:// for tests/local if redis is unavailable
import sys
is_testing = "pytest" in sys.modules

storage_uri = settings.redis_url
if is_testing or not storage_uri or not (storage_uri.startswith("redis://") or storage_uri.startswith("rediss://")):
    storage_uri = "memory://"


# Initialize limiter
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[RATE_LIMITS[RateLimitTier.READ]["list"]],  # Default: 300/min
    storage_uri=storage_uri,
    strategy="fixed-window",
    headers_enabled=False,
)


# =============================================================================
# RATE LIMIT DECORATORS
# =============================================================================

def rate_limit_auth(limit: str = RATE_LIMITS[RateLimitTier.AUTH]["login"]):
    """Apply auth-tier rate limit (very strict)."""
    return limiter.limit(limit)


def rate_limit_expensive(limit: str = RATE_LIMITS[RateLimitTier.EXPENSIVE]["simulation_run"]):
    """Apply expensive-tier rate limit."""
    return limiter.limit(limit)


def rate_limit_write(limit: str = RATE_LIMITS[RateLimitTier.WRITE]["create"]):
    """Apply write-tier rate limit."""
    return limiter.limit(limit)


def rate_limit_read(limit: str = RATE_LIMITS[RateLimitTier.READ]["list"]):
    """Apply read-tier rate limit."""
    return limiter.limit(limit)


# =============================================================================
# RATE LIMIT EXCEEDED HANDLER
# =============================================================================

async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """
    Handler for RateLimitExceeded.
    
    Returns 429 with Retry-After header and JSON error.
    """
    # Parse the limit string to get seconds (e.g., "5/minute" → 60s)
    retry_after = 60  # Default: 60 seconds
    limit_str = str(exc.detail)
    if "/minute" in limit_str:
        retry_after = 60
    elif "/hour" in limit_str:
        retry_after = 3600
    elif "/second" in limit_str:
        retry_after = 1
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "type": "https://api.cbms.in/errors/rate-limited",
            "title": "Too Many Requests",
            "status": 429,
            "detail": f"Rate limit exceeded: {exc.detail}",
            "instance": str(request.url.path),
            "retry_after_seconds": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
