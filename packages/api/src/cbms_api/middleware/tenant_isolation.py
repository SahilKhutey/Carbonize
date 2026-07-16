"""
Tenant isolation middleware.

Extracts organization context from JWT tokens and populates request state.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from cbms_api.auth.jwt_service import jwt_service, ACCESS_TOKEN
from cbms_shared.logging import get_logger


logger = get_logger(__name__)


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts the tenant org_id from the authorization token
    and stores it in the request state.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        request.state.org_id = None
        request.state.user = None
        
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
            try:
                payload = jwt_service.decode_token(token, ACCESS_TOKEN)
                request.state.org_id = payload.get("org_id")
            except Exception:
                # Let the route auth handler raise 401 if it requires auth
                pass
                
        response = await call_next(request)
        return response
