"""
Authentication routes: login, refresh, logout, MFA.
"""

from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
import secrets
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

import pyotp
from pyotp import TOTP
from cbms_api.middleware.rate_limiting import limiter, rate_limit_auth

from cbms_api.auth.jwt_service import jwt_service, ACCESS_TOKEN, REFRESH_TOKEN
from cbms_api.auth.password_service import password_service
from cbms_api.auth.rbac import get_current_active_user, AuthUser, get_current_user
from cbms_api.config import get_settings
from cbms_api.database.connection import get_db_session as get_db, set_tenant_context
from cbms_api.database.models import User as UserORM, RefreshToken as RefreshTokenORM, MFASecret as MFASecretORM
from cbms_api.audit.service import audit_service
from cbms_api.schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest, RefreshResponse,
    MFASetupRequest, MFASetupResponse, MFAVerifyRequest, PasswordChangeRequest,
    UserCreate, UserResponse,
)
from cbms_shared.exceptions import (
    AuthenticationError, ValidationFailedError, NotFoundError
)
from cbms_shared.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
@rate_limit_auth(limit="5/minute;20/hour")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access + refresh tokens.
    """
    # Find user
    result = await db.execute(
        select(UserORM).where(UserORM.email == body.email.lower())
    )
    user = result.scalar_one_or_none()
    
    # Always run password verify (timing-safe)
    if user is None:
        password_service.verify_password(body.password, "$2b$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalid")
        raise AuthenticationError("Invalid email or password")
    
    if not password_service.verify_password(body.password, user.hashed_password):
        await audit_service.log(
            org_id=user.organization_id,
            actor_id=str(user.id),
            event_type="auth.login_failed",
            ip_address=request.client.host if request.client else None,
        )
        raise AuthenticationError("Invalid email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is disabled")
    
    # Check MFA
    if user.mfa_enabled and settings.mfa_enabled:
        if not body.mfa_code:
            return LoginResponse(
                status="mfa_required",
                message="MFA code required",
                mfa_token=jwt_service.create_mfa_challenge_token(user.id, user.organization_id),
            )
        
        # Verify MFA
        mfa_result = await db.execute(
            select(MFASecretORM).where(MFASecretORM.user_id == user.id)
        )
        mfa_secret = mfa_result.scalar_one_or_none()
        if not mfa_secret:
            raise AuthenticationError("MFA not properly configured")
        
        totp = TOTP(mfa_secret.secret)
        if not totp.verify(body.mfa_code, valid_window=1):
            await audit_service.log(
                org_id=user.organization_id,
                actor_id=str(user.id),
                event_type="auth.mfa_failed",
                ip_address=request.client.host if request.client else None,
            )
            raise AuthenticationError("Invalid MFA code")
    
    # Set tenant context
    await set_tenant_context(db, str(user.organization_id))
    
    # Create tokens
    token_family = secrets.token_urlsafe(16)
    access_token = jwt_service.create_access_token(
        user_id=user.id,
        org_id=user.organization_id,
        roles=user.roles,
        email=user.email,
        mfa_verified=user.mfa_enabled,
    )
    refresh_token = jwt_service.create_refresh_token(
        user_id=user.id,
        org_id=user.organization_id,
        token_family=token_family,
    )
    
    # Store refresh token hash in DB
    refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db_refresh = RefreshTokenORM(
        id=uuid4(),
        user_id=user.id,
        organization_id=user.organization_id,
        token_hash=refresh_hash,
        token_family=token_family,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days),
    )
    db.add(db_refresh)
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host if request.client else None
    
    await db.commit()
    
    # Audit
    await audit_service.log(
        org_id=user.organization_id,
        actor_id=str(user.id),
        event_type="auth.login_success",
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"user_login user_id={user.id} org_id={user.organization_id}")
    
    return LoginResponse(
        status="success",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_ttl_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=RefreshResponse)
@rate_limit_auth(limit="30/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    """
    try:
        payload = jwt_service.decode_token(body.refresh_token, REFRESH_TOKEN)
    except AuthenticationError:
        raise AuthenticationError("Invalid refresh token")
    
    user_id = UUID(payload["sub"])
    org_id = UUID(payload["org_id"])
    family = payload["family"]
    
    # Check if this token is in our DB and not revoked
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshTokenORM).where(
            RefreshTokenORM.token_hash == token_hash,
            RefreshTokenORM.revoked == False,
        )
    )
    stored_token = result.scalar_one_or_none()
    
    if stored_token is None:
        # Token reuse detected! Revoke entire family
        await db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.token_family == family)
            .values(revoked=True)
        )
        await db.commit()
        raise AuthenticationError("Refresh token reuse detected; all sessions revoked")
    
    # Revoke old token
    stored_token.revoked = True
    
    # Get user to construct access token
    user = await db.get(UserORM, user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User is no longer active")
        
    # Create new tokens
    new_access = jwt_service.create_access_token(
        user_id=user.id,
        org_id=user.organization_id,
        roles=user.roles,
        email=user.email,
        mfa_verified=user.mfa_enabled,
    )
    new_refresh = jwt_service.create_refresh_token(
        user_id=user.id,
        org_id=user.organization_id,
        token_family=family,
    )
    
    # Store new refresh token
    new_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    db.add(RefreshTokenORM(
        id=uuid4(),
        user_id=user.id,
        organization_id=user.organization_id,
        token_hash=new_hash,
        token_family=family,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days),
    ))
    
    await db.commit()
    
    return RefreshResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_ttl_minutes * 60,
    )


@router.post("/logout", status_code=204)
@rate_limit_auth(limit="10/minute")
async def logout(
    request: Request,
    user: AuthUser = Depends(get_current_active_user),
    body: RefreshRequest = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout: revoke the refresh token.
    """
    if body and body.refresh_token:
        token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
        await db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.token_hash == token_hash)
            .values(revoked=True)
        )
    
    # Revoke all tokens for this user
    await db.execute(
        update(RefreshTokenORM)
        .where(RefreshTokenORM.user_id == user.user_id, RefreshTokenORM.revoked == False)
        .values(revoked=True)
    )
    await db.commit()
    
    await audit_service.log(
        org_id=user.org_id,
        actor_id=str(user.user_id),
        event_type="auth.logout",
    )
    
    return Response(status_code=204)


@router.post("/mfa/setup", response_model=MFASetupResponse)
@rate_limit_auth(limit="10/minute")
async def mfa_setup(
    request: Request,
    body: MFASetupRequest,
    user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Set up TOTP MFA for the current user."""
    # Generate secret
    secret = pyotp.random_base32()
    
    # Store in DB
    existing = await db.execute(
        select(MFASecretORM).where(MFASecretORM.user_id == user.user_id)
    )
    mfa_record = existing.scalar_one_or_none()
    if mfa_record is None:
        mfa_record = MFASecretORM(user_id=user.user_id, secret=secret)
        db.add(mfa_record)
    else:
        mfa_record.secret = secret
    
    # Generate backup codes
    backup_codes = [secrets.token_urlsafe(8) for _ in range(settings.mfa_backup_codes_count)]
    mfa_record.backup_codes = backup_codes
    
    await db.commit()
    
    # Generate provisioning URI
    totp = TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name=settings.mfa_issuer,
    )
    
    return MFASetupResponse(
        secret=secret,
        provisioning_uri=provisioning_uri,
        backup_codes=backup_codes,
    )


@router.post("/mfa/verify", status_code=204)
@rate_limit_auth(limit="10/minute")
async def mfa_verify(
    request: Request,
    body: MFAVerifyRequest,
    user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify a TOTP code and enable MFA on the account."""
    result = await db.execute(
        select(MFASecretORM).where(MFASecretORM.user_id == user.user_id)
    )
    mfa_record = result.scalar_one_or_none()
    if mfa_record is None:
        raise NotFoundError("MFA not set up; call /mfa/setup first")
    
    totp = TOTP(mfa_record.secret)
    if not totp.verify(body.code, valid_window=1):
        raise AuthenticationError("Invalid MFA code")
    
    # Enable MFA
    user_record = await db.get(UserORM, user.user_id)
    user_record.mfa_enabled = True
    await db.commit()


@router.post("/password", status_code=204)
@rate_limit_auth(limit="3/hour")
async def change_password(
    request: Request,
    body: PasswordChangeRequest,
    user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password."""
    # Validate new password strength
    password_service.validate_password_strength(body.new_password)
    
    # Verify current password
    user_record = await db.get(UserORM, user.user_id)
    if not password_service.verify_password(body.current_password, user_record.hashed_password):
        raise AuthenticationError("Current password is incorrect")
    
    # Hash and store
    user_record.hashed_password = password_service.hash_password(body.new_password)
    user_record.password_changed_at = datetime.now(timezone.utc)
    
    # Revoke all refresh tokens (force re-login)
    await db.execute(
        update(RefreshTokenORM)
        .where(RefreshTokenORM.user_id == user.user_id, RefreshTokenORM.revoked == False)
        .values(revoked=True)
    )
    
    await db.commit()
    
    await audit_service.log(
        org_id=user.org_id,
        actor_id=str(user.user_id),
        event_type="auth.password_changed",
    )
