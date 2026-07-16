"""
Role-Based Access Control (RBAC) with permission decorators.
"""

from enum import Enum
from functools import wraps
from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from cbms_api.auth.jwt_service import jwt_service, ACCESS_TOKEN
from cbms_shared.exceptions import AuthorizationError
from cbms_shared.logging import get_logger
from cbms_api.config import get_settings


logger = get_logger(__name__)
settings = get_settings()


class Role(str, Enum):
    """Organization roles (ordered by privilege)."""
    OWNER = "owner"
    ADMIN = "admin"
    ENGINEER = "engineer"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Permission matrix
PERMISSIONS = {
    # Plants
    "plants:read": {Role.OWNER, Role.ADMIN, Role.ENGINEER, Role.ANALYST, Role.VIEWER},
    "plants:write": {Role.OWNER, Role.ADMIN, Role.ENGINEER},
    "plants:delete": {Role.OWNER, Role.ADMIN},
    
    # Simulations
    "simulations:read": {Role.OWNER, Role.ADMIN, Role.ENGINEER, Role.ANALYST, Role.VIEWER},
    "simulations:run": {Role.OWNER, Role.ADMIN, Role.ENGINEER},
    "simulations:cancel": {Role.OWNER, Role.ADMIN, Role.ENGINEER},
    "simulations:delete": {Role.OWNER, Role.ADMIN},
    
    # Reports
    "reports:read": {Role.OWNER, Role.ADMIN, Role.ENGINEER, Role.ANALYST, Role.VIEWER},
    "reports:generate": {Role.OWNER, Role.ADMIN, Role.ENGINEER},
    
    # Compliance
    "compliance:read": {Role.OWNER, Role.ADMIN, Role.ANALYST, Role.VIEWER},
    "compliance:submit": {Role.OWNER, Role.ADMIN},
    
    # Admin
    "users:read": {Role.OWNER, Role.ADMIN},
    "users:write": {Role.OWNER, Role.ADMIN},
    "users:invite": {Role.OWNER, Role.ADMIN},
    "users:delete": {Role.OWNER},
    
    # Billing
    "billing:read": {Role.OWNER},
    "billing:write": {Role.OWNER},
    
    # API keys
    "api_keys:read": {Role.OWNER, Role.ADMIN},
    "api_keys:write": {Role.OWNER, Role.ADMIN},
    "api_keys:delete": {Role.OWNER, Role.ADMIN},
}


def has_permission(user_roles: list[str], permission: str) -> bool:
    """Check if any of the user's roles has the required permission."""
    allowed_roles = PERMISSIONS.get(permission, set())
    user_role_set = set(user_roles)
    return bool(user_role_set & allowed_roles)


class AuthUser:
    """Authenticated user context."""
    
    def __init__(
        self,
        user_id: UUID,
        org_id: UUID,
        email: str,
        roles: list[str],
        mfa_verified: bool,
    ):
        self.user_id = user_id
        self.org_id = org_id
        self.email = email
        self.roles = roles
        self.mfa_verified = mfa_verified
    
    def has_role(self, role: Role) -> bool:
        return role.value in self.roles
    
    def has_permission(self, permission: str) -> bool:
        return has_permission(self.roles, permission)
    
    def __repr__(self):
        return f"AuthUser(id={self.user_id}, org={self.org_id}, roles={self.roles})"


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthUser:
    """
    FastAPI dependency: extract authenticated user from request.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt_service.decode_token(credentials.credentials, ACCESS_TOKEN)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = AuthUser(
        user_id=UUID(payload["sub"]),
        org_id=UUID(payload["org_id"]),
        email=payload["email"],
        roles=payload["roles"],
        mfa_verified=payload.get("mfa", False),
    )
    
    # Store in request state for middleware/database sessions
    request.state.user = user
    request.state.org_id = user.org_id
        
    return user


async def get_current_active_user(
    user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """Get current user and verify MFA if required."""
    if settings.mfa_enabled:
        required_roles = settings.mfa_required_roles
        if any(role in user.roles for role in required_roles):
            if not user.mfa_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="MFA required for this role",
                )
    
    return user


def require_permission(permission: str) -> Callable:
    """
    Decorator factory: require a specific permission.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, user: AuthUser = None, **kwargs):
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            if not user.has_permission(permission):
                logger.warning(
                    "permission_denied",
                    user_id=str(user.user_id),
                    permission=permission,
                    roles=user.roles,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}",
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role) -> Callable:
    """Decorator factory: require a specific role."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, user: AuthUser = None, **kwargs):
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            if not user.has_role(role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role.value}",
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator
