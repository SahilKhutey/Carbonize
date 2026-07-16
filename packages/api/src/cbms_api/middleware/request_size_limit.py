"""
Limit request body size to prevent DoS via large payloads.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from cbms_api.rate_limits import REQUEST_SIZE_LIMITS


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that rejects requests with body > max allowed size.
    
    Returns 413 (Payload Too Large) before the body is fully read.
    """
    
    def __init__(self, app, default_max_mb: float = 1.0):
        super().__init__(app)
        self.default_max_bytes = int(default_max_mb * 1024 * 1024)
    
    async def dispatch(self, request, call_next):
        # Determine max size for this endpoint
        max_bytes = self._get_max_size_for_path(request.url.path)
        
        # Check Content-Length header (fast path)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > max_bytes:
                    return self._reject_too_large(
                        request, int(content_length), max_bytes
                    )
            except ValueError:
                pass  # Malformed header
        
        return await call_next(request)
    
    def _get_max_size_for_path(self, path: str) -> int:
        """Determine max body size for this path."""
        for key, size_mb in REQUEST_SIZE_LIMITS.items():
            if not isinstance(size_mb, (int, float)):
                continue
            # Check if key is in path, e.g. "auth" or "simulation"
            # Map clean terms in limits config to paths
            term = key.split("_")[0]
            if term in path:
                return int(size_mb * 1024 * 1024)
        return self.default_max_bytes
    
    def _reject_too_large(self, request, size: int, max_size: int):
        return JSONResponse(
            status_code=413,
            content={
                "type": "https://api.cbms.in/errors/payload-too-large",
                "title": "Payload Too Large",
                "status": 413,
                "detail": f"Request body {size} bytes exceeds maximum {max_size} bytes",
                "instance": str(request.url.path),
            },
        )
