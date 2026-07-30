"""
Multi-Region Gateway with Automatic Failover
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import httpx
from contextlib import asynccontextmanager


class RegionStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


@dataclass
class RegionHealth:
    """Health state for a single region."""
    region_id: str
    endpoint: str
    status: RegionStatus = RegionStatus.UNHEALTHY
    latency_ms: float = 0.0
    error_rate: float = 0.0
    last_check: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    active_connections: int = 0


class HealthCheckConfig:
    HEALTHY_ERROR_THRESHOLD = 0.05
    HEALTHY_LATENCY_THRESHOLD_MS = 200
    DEGRADED_ERROR_THRESHOLD = 0.20
    CHECK_INTERVAL_SEC = 5
    TIMEOUT_SEC = 3
    REQUIRED_SUCCESSES = 2
    REQUIRED_FAILURES = 3


@dataclass
class RouteConfig:
    """Routing configuration."""
    strategy: str = 'latency_based'      # or 'weighted', 'geo'
    weights: Dict[str, float] = field(default_factory=dict)
    geo_routes: Dict[str, str] = field(default_factory=dict)
    sticky_sessions: bool = True


class GeoRouter:
    """
    Geo-distributed gateway with automatic failover.
    
    Routing strategies:
        - latency_based: Route to lowest latency
        - weighted: Route by ratio (for canary deployments)
        - geo: Route by user location
    """
    
    def __init__(self, config: RouteConfig):
        self.config = config
        self.regions: Dict[str, RegionHealth] = {}
        self.logger = logging.getLogger('geo-router')
        self._client = httpx.AsyncClient(timeout=HealthCheckConfig.TIMEOUT_SEC)
        self._running = False
        self._user_region_cache: Dict[str, str] = {}
    
    def register_region(self, region_id: str, endpoint: str):
        """Register a region."""
        self.regions[region_id] = RegionHealth(
            region_id=region_id,
            endpoint=endpoint
        )
        self.logger.info(f"Registered region: {region_id} -> {endpoint}")
    
    async def start_health_checks(self):
        """Background health check loop."""
        self._running = True
        while self._running:
            await self._check_all_regions()
            await asyncio.sleep(HealthCheckConfig.CHECK_INTERVAL_SEC)
    
    async def _check_all_regions(self):
        """Check health of all regions concurrently."""
        tasks = [
            self._check_region(region_id)
            for region_id in self.regions
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_region(self, region_id: str):
        """Check health of a single region."""
        region = self.regions[region_id]
        
        try:
            start = time.perf_counter()
            response = await self._client.get(
                f"{region.endpoint}/v1/health/ready",
                timeout=HealthCheckConfig.TIMEOUT_SEC
            )
            latency_ms = (time.perf_counter() - start) * 1000
            
            if response.status_code == 200:
                region.latency_ms = latency_ms
                region.consecutive_failures = 0
                region.consecutive_successes += 1
                region.last_check = time.time()
                
                if latency_ms > HealthCheckConfig.HEALTHY_LATENCY_THRESHOLD_MS:
                    region.status = RegionStatus.DEGRADED
                else:
                    region.status = RegionStatus.HEALTHY
            else:
                region.consecutive_failures += 1
                region.consecutive_successes = 0
                if region.consecutive_failures >= HealthCheckConfig.REQUIRED_FAILURES:
                    region.status = RegionStatus.UNHEALTHY
        except Exception as e:
            region.consecutive_failures += 1
            region.consecutive_successes = 0
            self.logger.warning(f"Health check failed for {region_id}: {e}")
            if region.consecutive_failures >= HealthCheckConfig.REQUIRED_FAILURES:
                region.status = RegionStatus.UNHEALTHY
    
    async def route_request(self, request) -> str:
        """Route request to best region."""
        user_id = self._get_user_id(request)
        user_location = self._get_user_location(request)
        
        if self.config.sticky_sessions and user_id in self._user_region_cache:
            cached_region = self._user_region_cache[user_id]
            if self.regions.get(cached_region, {}).status != RegionStatus.UNHEALTHY:
                return cached_region
        
        healthy_regions = [
            r for r in self.regions.values()
            if r.status in [RegionStatus.HEALTHY, RegionStatus.DEGRADED]
        ]
        
        if not healthy_regions:
            self.logger.error("All regions unhealthy!")
            if self.regions:
                fallback = next(iter(self.regions.values()))
                return fallback.region_id
            raise RuntimeError("No regions available")
        
        if self.config.strategy == 'geo':
            region = self._route_by_geo(user_location, healthy_regions)
        elif self.config.strategy == 'weighted':
            region = self._route_by_weight(healthy_regions)
        else:
            region = self._route_by_latency(healthy_regions)
        
        if self.config.sticky_sessions and user_id:
            self._user_region_cache[user_id] = region.region_id
        
        return region.region_id
    
    def _route_by_latency(self, regions: List[RegionHealth]) -> RegionHealth:
        """Route to lowest latency region."""
        return min(regions, key=lambda r: r.latency_ms)
    
    def _route_by_weight(self, regions: List[RegionHealth]) -> RegionHealth:
        """Route by configured weights."""
        import random
        weights = [self.config.weights.get(r.region_id, 1.0) for r in regions]
        return random.choices(regions, weights=weights)[0]
    
    def _route_by_geo(self, location: str, 
                      regions: List[RegionHealth]) -> RegionHealth:
        """Route by geographic proximity."""
        preferred = self.config.geo_routes.get(location)
        for region in regions:
            if region.region_id == preferred:
                return region
        return self._route_by_latency(regions)
    
    def _get_user_id(self, request) -> Optional[str]:
        return getattr(request, 'headers', {}).get('X-User-ID')
    
    def _get_user_location(self, request) -> str:
        return getattr(request, 'headers', {}).get('CF-IPCountry', 'US')
    
    def get_status(self) -> Dict:
        """Get current router status."""
        return {
            'regions': {
                rid: {
                    'status': r.status.value,
                    'latency_ms': r.latency_ms,
                    'error_rate': r.error_rate,
                    'active_connections': r.active_connections
                }
                for rid, r in self.regions.items()
            },
            'strategy': self.config.strategy,
            'active_users': len(self._user_region_cache)
        }
    
    async def close(self):
        self._running = False
        await self._client.aclose()
