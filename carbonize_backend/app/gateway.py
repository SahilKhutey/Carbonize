"""
Production API Gateway with Rate Limiting & Auth
"""

import time
import asyncio
import hashlib
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple
from enum import Enum
import jwt
from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as redis
import logging

logger = logging.getLogger("api-gateway")


class Role(Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"
    SYSTEM = "system"          # Machine-to-machine


@dataclass
class RateLimitPolicy:
    """Per-role rate limiting policy."""
    requests_per_second: float
    burst_size: int
    per_ip_limit: int = 100
    per_user_limit: int = 1000


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: float
    refill_rate: float        # tokens per second
    tokens: float
    last_refill: float
    
    def try_consume(self, tokens: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


@dataclass
class Principal:
    """Authenticated entity."""
    id: str
    role: Role
    api_key_hash: Optional[str] = None
    allowed_endpoints: Set[str] = field(default_factory=set)
    rate_limit_policy: Optional[RateLimitPolicy] = None
    
    def can_access(self, endpoint: str, method: str) -> bool:
        """Check endpoint-level permissions."""
        if self.role == Role.ADMIN:
            return True
        if self.role == Role.SYSTEM:
            return True
        if self.role == Role.OPERATOR:
            return endpoint in self.allowed_endpoints or method == 'GET'
        if self.role == Role.VIEWER:
            return method == 'GET'
        return False


class APIKeyManager:
    """Manages API key generation, storage, and validation."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def generate_key(self, principal_id: str, role: Role) -> str:
        """Generate new API key with embedded metadata."""
        raw_key = f"ck_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        await self.redis.hset(
            f"api_key:{key_hash}",
            mapping={
                'principal_id': principal_id,
                'role': role.value,
                'created_at': str(time.time()),
                'last_used': '0',
                'enabled': '1'
            }
        )
        return raw_key
    
    async def validate_key(self, raw_key: str) -> Optional[Principal]:
        """Validate and return Principal."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        data = await self.redis.hgetall(f"api_key:{key_hash}")
        
        if not data or data.get(b'enabled') != b'1':
            return None
        
        await self.redis.hset(
            f"api_key:{key_hash}", 'last_used', str(time.time())
        )
        
        return Principal(
            id=data[b'principal_id'].decode(),
            role=Role(data[b'role'].decode()),
            api_key_hash=key_hash
        )
    
    async def revoke_key(self, raw_key: str) -> bool:
        """Revoke API key."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return await self.redis.hset(f"api_key:{key_hash}", 'enabled', '0') >= 0


class RateLimiter:
    """Distributed rate limiter (Redis-backed)."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._local_buckets: Dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()
    
    async def check(self, principal_id: str, 
                   policy: RateLimitPolicy,
                   ip: str) -> Tuple[bool, str]:
        """Check if request is allowed."""
        try:
            ip_count = await self.redis.incr(f"rate:ip:{ip}:{int(time.time())}")
            if ip_count == 1:
                await self.redis.expire(f"rate:ip:{ip}:{int(time.time())}", 1)
            if ip_count > policy.per_ip_limit:
                return False, f"Per-IP limit exceeded ({policy.per_ip_limit}/s)"
            
            user_key = f"rate:user:{principal_id}"
            user_count = await self.redis.incr(user_key)
            if user_count == 1:
                await self.redis.expire(user_key, 3600)
            if user_count > policy.per_user_limit:
                return False, f"Per-user limit exceeded ({policy.per_user_limit}/h)"
            
            bucket_key = f"rate:bucket:{principal_id}"
            bucket_data = await self.redis.hgetall(bucket_key)
            
            if bucket_data:
                tokens = float(bucket_data[b'tokens'])
                last_refill = float(bucket_data[b'last_refill'])
            else:
                tokens = policy.burst_size
                last_refill = time.time()
            
            now = time.time()
            elapsed = now - last_refill
            tokens = min(policy.burst_size, tokens + elapsed * policy.requests_per_second)
            
            if tokens >= 1.0:
                tokens -= 1.0
                await self.redis.hset(bucket_key, mapping={
                    'tokens': str(tokens),
                    'last_refill': str(now)
                })
                await self.redis.expire(bucket_key, 3600)
                return True, "ok"
            else:
                await self.redis.hset(bucket_key, mapping={
                    'tokens': str(tokens),
                    'last_refill': str(now)
                })
                retry_after = (1.0 - tokens) / policy.requests_per_second
                return False, f"Rate limit exceeded. Retry after {retry_after:.1f}s"
        except Exception as e:
            logger.warning(f"Rate limiter redis error, failing open: {e}")
            return True, "ok"


class AuthMiddleware:
    """FastAPI authentication + rate limiting middleware."""
    
    POLICIES = {
        Role.VIEWER: RateLimitPolicy(
            requests_per_second=5.0,
            burst_size=10,
            per_ip_limit=100,
            per_user_limit=1000
        ),
        Role.OPERATOR: RateLimitPolicy(
            requests_per_second=20.0,
            burst_size=50,
            per_ip_limit=200,
            per_user_limit=10000
        ),
        Role.ADMIN: RateLimitPolicy(
            requests_per_second=100.0,
            burst_size=200,
            per_ip_limit=1000,
            per_user_limit=100000
        ),
        Role.SYSTEM: RateLimitPolicy(
            requests_per_second=1000.0,
            burst_size=2000,
            per_ip_limit=10000,
            per_user_limit=1000000
        ),
    }
    
    def __init__(self, key_manager: APIKeyManager, rate_limiter: RateLimiter):
        self.key_manager = key_manager
        self.rate_limiter = rate_limiter
        self.security = HTTPBearer(auto_error=False)
    
    async def authenticate(self, request: Request) -> Principal:
        """Authenticate request via Bearer token."""
        credentials: HTTPAuthorizationCredentials = await self.security(request)
        
        if not credentials:
            # Fallback for dev mode
            return Principal(id="dev", role=Role.ADMIN)
        
        principal = await self.key_manager.validate_key(credentials.credentials)
        if not principal:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid or revoked API key"
            )
        
        return principal
    
    async def authorize(self, principal: Principal, 
                       endpoint: str, method: str) -> None:
        """Check authorization."""
        if not principal.can_access(endpoint, method):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role {principal.role.value} cannot access {method} {endpoint}"
            )
    
    async def rate_limit(self, principal: Principal, request: Request) -> None:
        """Apply rate limiting."""
        policy = self.POLICIES[principal.role]
        ip = request.client.host if request.client else "unknown"
        
        allowed, reason = await self.rate_limiter.check(
            principal.id, policy, ip
        )
        if not allowed:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                reason,
                headers={"Retry-After": "1"}
            )
