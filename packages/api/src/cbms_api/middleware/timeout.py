"""
Request timeout middleware to prevent slow loris attacks.
"""

import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from cbms_api.rate_limits import REQUEST_TIMEOUTS


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Abort requests that take longer than the per-endpoint timeout."""
    
    def __init__(self, app, default_timeout: float = 30.0):
        super().__init__(app)
        self.default_timeout = default_timeout
    
    async def dispatch(self, request, call_next):
        timeout = self._get_timeout_for_path(request.url.path)
        
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "type": "https://api.cbms.in/errors/timeout",
                    "title": "Gateway Timeout",
                    "status": 504,
                    "detail": f"Request exceeded {timeout}s timeout",
                    "instance": str(request.url.path),
                },
            )
    
    def _get_timeout_for_path(self, path: str) -> float:
        """Determine timeout for this path."""
        for key, timeout in REQUEST_TIMEOUTS.items():
            # Match prefixes/terms, e.g. "simulation" or "report"
            term = key.split("_")[0]
            if term in path:
                return float(timeout)
        return self.default_timeout
