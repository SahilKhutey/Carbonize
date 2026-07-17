"""
Integration tests for authentication and multi-tenant isolation.
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# MONKEYPATCH BCRYPT TO FIX PASSLIB 72-BYTE PASSWORD LIMITATION IN NEWER BCRYPT
# -----------------------------------------------------------------------------
import bcrypt
_original_hashpw = bcrypt.hashpw
def _safe_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    elif isinstance(password, str) and len(password.encode('utf-8')) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = _safe_hashpw
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# MONKEYPATCH DATABASE CONFIGURATION FOR IN-MEMORY SQLITE TESTING
# -----------------------------------------------------------------------------
import cbms_api.database.connection as conn_mod
import database.connection as conn_mod_alt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Overwrite database URL and async engine to SQLite memory for self-contained tests
from sqlalchemy.pool import StaticPool
sqlite_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
sqlite_sessionmaker = async_sessionmaker(
    bind=sqlite_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Apply monkeypatching before importing app/routes
conn_mod.engine = sqlite_test_engine
conn_mod.async_session_maker = sqlite_sessionmaker

conn_mod_alt.engine = sqlite_test_engine
conn_mod_alt.async_session_maker = sqlite_sessionmaker
# -----------------------------------------------------------------------------

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from cbms_api.api.main import app
from cbms_api.config import get_settings
from cbms_api.database.models import User, Organization, PlantProfile
from cbms_api.database.connection import async_session_maker
from cbms_api.auth.password_service import password_service
from cbms_api.auth.jwt_service import jwt_service


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def setup_test_data():
    """Seed two distinct organizations and users to verify RLS isolation."""
    # Ensure a completely clean slate for each integration test
    from cbms_api.database.models import Base
    async with conn_mod.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Create Org A
        org_a = Organization(
            id=uuid4(),
            name="Org A",
            industry_type="Cement",
        )
        # Create Org B
        org_b = Organization(
            id=uuid4(),
            name="Org B",
            industry_type="Power",
        )
        session.add_all([org_a, org_b])
        await session.flush()

        # Create Users
        hashed_pwd = password_service.hash_password("SuperSecret!123")
        
        user_a = User(
            id=uuid4(),
            organization_id=org_a.id,
            email="user_a@orga.com",
            hashed_password=hashed_pwd,
            roles=["engineer"],
            is_active=True,
        )
        
        user_b = User(
            id=uuid4(),
            organization_id=org_b.id,
            email="user_b@orgb.com",
            hashed_password=hashed_pwd,
            roles=["engineer"],
            is_active=True,
        )
        
        session.add_all([user_a, user_b])
        await session.flush()
        
        # Create Plant A (belongs to Org A)
        plant_a = PlantProfile(
            id=uuid4(),
            organization_id=org_a.id,
            name="Plant A",
            location="A-City",
            boiler_type="Pulverized",
            exhaust_flow_rate=12000.0,
            baseline_temperature=145.0,
            co2_concentration=14.0,
            so2_concentration=1100.0,
            fly_ash_load=45.0,
            nox_concentration=500.0,
        )
        session.add(plant_a)
        await session.commit()
        
        return {
            "org_a": org_a,
            "org_b": org_b,
            "user_a": user_a,
            "user_b": user_b,
            "plant_a": plant_a,
        }


@pytest.mark.anyio
async def test_login_success(client, setup_test_data):
    """Verify login authenticates correctly and generates tokens."""
    data = setup_test_data
    
    # Attempt login
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "user_a@orga.com",
            "password": "SuperSecret!123",
        }
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert "access_token" in res_data
    assert "refresh_token" in res_data
    assert res_data["user"]["email"] == "user_a@orga.com"


@pytest.mark.anyio
async def test_login_invalid_password(client, setup_test_data):
    """Verify invalid password returns AuthenticationError status."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "user_a@orga.com",
            "password": "WrongPassword123",
        }
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_mfa_flow(client, setup_test_data):
    """Verify TOTP MFA setup and verification endpoints."""
    data = setup_test_data
    
    # Generate token
    token = jwt_service.create_access_token(
        user_id=data["user_a"].id,
        org_id=data["org_a"].id,
        roles=["engineer"],
        email="user_a@orga.com",
        mfa_verified=True,
    )
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Setup TOTP MFA
    setup_response = await client.post(
        "/api/auth/mfa/setup",
        json={},
        headers=headers
    )
    assert setup_response.status_code == 200
    setup_data = setup_response.json()
    assert "secret" in setup_data
    assert "provisioning_uri" in setup_data
    
    # 2. Verify MFA code (invalid code)
    verify_response = await client.post(
        "/api/auth/mfa/verify",
        json={"code": "000000"},
        headers=headers
    )
    assert verify_response.status_code == 401
    
    # 3. Enable MFA on user record to verify login challenge
    async with async_session_maker() as session:
        user = await session.get(User, data["user_a"].id)
        user.mfa_enabled = True
        await session.commit()
        
    # Login again, should trigger challenge
    login_challenge = await client.post(
        "/api/auth/login",
        json={
            "email": "user_a@orga.com",
            "password": "SuperSecret!123",
        }
    )
    assert login_challenge.status_code == 200
    challenge_data = login_challenge.json()
    assert challenge_data["status"] == "mfa_required"
    assert "mfa_token" in challenge_data


@pytest.mark.anyio
async def test_tenant_isolation_rls(client, setup_test_data):
    """
    CRITICAL SECURITY CHECK:
    Verify Row-Level Security (RLS) and tenant isolation prevents User B
    from seeing or accessing Plant A, which belongs to Org A.
    """
    data = setup_test_data
    
    # User B Token
    token_b = jwt_service.create_access_token(
        user_id=data["user_b"].id,
        org_id=data["org_b"].id,
        roles=["engineer"],
        email="user_b@orgb.com",
        mfa_verified=True,
    )
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # User B queries plants - should NOT return Plant A
    response = await client.get("/api/plants", headers=headers_b)
    assert response.status_code == 200
    plants = response.json()
    
    # Check that none of the returned plants are Plant A
    plant_ids = [p["id"] for p in plants] if plants else []
    assert str(data["plant_a"].id) not in plant_ids, \
        "RLS BREACH: User B could read Plant A belonging to Org A!"


@pytest.mark.anyio
async def test_invalid_and_missing_auth(client, setup_test_data):
    """Verify missing or malformed authentication headers reject appropriately."""
    # No auth
    response = await client.get("/api/plants")
    assert response.status_code == 401
    
    # Invalid scheme (Basic instead of Bearer)
    response = await client.get("/api/plants", headers={"Authorization": "Basic 123"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_jwt_validation_and_token_rotation(client, setup_test_data):
    """Verify token refresh rotation and token reuse detection logic."""
    # Login to get valid refresh token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "user_a@orga.com",
            "password": "SuperSecret!123",
        }
    )
    res_data = login_response.json()
    refresh_token = res_data["refresh_token"]
    
    # 1. Rotate token (exchange old refresh for new pair)
    rotate_response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert rotate_response.status_code == 200
    rotate_data = rotate_response.json()
    assert "access_token" in rotate_data
    assert "refresh_token" in rotate_data
    
    # 2. Attempt to reuse old refresh token - should fail and revoke family
    reuse_response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert reuse_response.status_code == 401


@pytest.mark.anyio
async def test_mfa_requirement_for_admin_role(client, setup_test_data):
    """Verify roles in mfa_required_roles are forbidden if access token mfa=False."""
    data = setup_test_data
    
    # Setup admin user
    async with async_session_maker() as session:
        user = await session.get(User, data["user_a"].id)
        user.roles = ["admin"]
        user.mfa_enabled = True
        await session.commit()
        
    # Generate access token with mfa=False
    token = jwt_service.create_access_token(
        user_id=data["user_a"].id,
        org_id=data["org_a"].id,
        roles=["admin"],
        email="user_a@orga.com",
        mfa_verified=False,
    )
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/plants", headers=headers)
    # Should get 403 Forbidden due to unverified MFA for admin role
    assert response.status_code == 403


@pytest.mark.anyio
async def test_rbac_decorators():
    """Verify require_role and require_permission decorators enforce security rules."""
    from cbms_api.auth.rbac import require_role, require_permission, Role, AuthUser
    
    @require_role(Role.ADMIN)
    async def dummy_admin_route(user: AuthUser = None):
        return "success"
        
    @require_permission("plants:delete")
    async def dummy_permission_route(user: AuthUser = None):
        return "success"
        
    # Setup test users
    user_analyst = AuthUser(uuid4(), uuid4(), "analyst@test.com", ["analyst"], True)
    user_admin = AuthUser(uuid4(), uuid4(), "admin@test.com", ["admin"], True)
    
    # 1. require_role rejects analyst, accepts admin
    with pytest.raises(Exception) as exc:
        await dummy_admin_route(user=user_analyst)
    assert "Role required" in str(exc.value)
    
    res = await dummy_admin_route(user=user_admin)
    assert res == "success"
    
    # 2. require_permission rejects analyst, accepts admin (plants:delete is restricted to owner/admin)
    with pytest.raises(Exception) as exc:
        await dummy_permission_route(user=user_analyst)
    assert "Permission denied" in str(exc.value)
    
    res = await dummy_permission_route(user=user_admin)
    assert res == "success"


@pytest.mark.anyio
async def test_jwt_validation_errors():
    """Verify decode_token raises AuthenticationError for malformed/invalid tokens."""
    from cbms_api.auth.jwt_service import jwt_service, ACCESS_TOKEN
    from cbms_shared.exceptions import AuthenticationError
    
    # 1. Malformed token
    with pytest.raises(AuthenticationError) as exc:
        jwt_service.decode_token("not-a-valid-token-string", ACCESS_TOKEN)
    assert "Invalid token" in str(exc.value)
    
    # 2. Wrong token type (sending refresh token to access token decoder)
    refresh_token = jwt_service.create_refresh_token(uuid4(), uuid4(), "family123")
    with pytest.raises(AuthenticationError) as exc:
        jwt_service.decode_token(refresh_token, ACCESS_TOKEN)
    assert "Wrong token type" in str(exc.value)


