"""
Pydantic schemas for authentication and user management.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request payload for logging in."""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None


class UserResponse(BaseModel):
    """User representation in responses."""
    id: UUID
    email: str
    roles: List[str]
    is_active: bool
    mfa_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response payload for successful login or MFA challenge."""
    status: str = "success"  # "success" or "mfa_required"
    message: Optional[str] = None
    mfa_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_in: Optional[int] = None
    user: Optional[UserResponse] = None


class RefreshRequest(BaseModel):
    """Request payload for token refresh."""
    refresh_token: str


class RefreshResponse(BaseModel):
    """Response payload for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MFASetupRequest(BaseModel):
    """Request payload for MFA setup."""
    pass


class MFASetupResponse(BaseModel):
    """Response payload for MFA setup."""
    secret: str
    provisioning_uri: str
    backup_codes: List[str]


class MFAVerifyRequest(BaseModel):
    """Request payload for MFA verification."""
    code: str


class PasswordChangeRequest(BaseModel):
    """Request payload for changing password."""
    current_password: str
    new_password: str


class UserCreate(BaseModel):
    """Request payload for creating a user."""
    email: EmailStr
    password: str
    roles: List[str] = Field(default_factory=lambda: ["viewer"])
    organization_id: UUID
