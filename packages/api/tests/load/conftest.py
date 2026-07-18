"""
Load test configuration: setup for burst traffic tests.
"""

import pytest
import asyncio
import secrets
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta

# -----------------------------------------------------------------------------
# MONKEYPATCH BCRYPT FOR IN-MEMORY SQLITE TESTING
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

import cbms_api.database.connection as conn_mod
from sqlalchemy.ext.asyncio import AsyncSession

# Mock Celery delay calls to avoid connecting to Redis or running slow tasks in load tests
from unittest.mock import MagicMock
try:
    from cbms_workers.workers.tasks import run_simulation_task, generate_report
    run_simulation_task.delay = MagicMock(return_value=MagicMock(id="mock-task-id"))
    generate_report.delay = MagicMock(return_value=MagicMock(id="mock-report-task-id"))
except Exception:
    pass
# -----------------------------------------------------------------------------

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from cbms_api.api.main import app
from cbms_api.database.models import Base, Organization, User, PlantProfile, LogisticsConfig
from cbms_api.database.connection import async_session_maker
from cbms_api.auth.password_service import password_service
from cbms_api.auth.jwt_service import jwt_service


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    """Async HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def setup_load_data():
    """Ensure clean table structures and seed 10 tenants with 10 users each."""
    async with conn_mod.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session_maker() as session:
        users = []
        tenants = []
        
        for tenant_i in range(10):
            # Create organization
            org = Organization(
                id=uuid4(),
                name=f"Load Test Org {tenant_i}",
                industry_type="Cement",
            )
            session.add(org)
            await session.flush()
            tenants.append(org)
            
            # Create a plant for this org
            plant = PlantProfile(
                id=uuid4(),
                organization_id=org.id,
                name=f"Load Test Plant {tenant_i}",
                location="Maharashtra",
                boiler_type="pulverized",
                exhaust_flow_rate=10000.0,
                baseline_temperature=150.0,
                co2_concentration=14.0,
                so2_concentration=1200.0,
                fly_ash_load=45.0,
                nox_concentration=500.0,
            )
            session.add(plant)
            await session.flush()
            
            # Create logistics
            logistics = LogisticsConfig(
                id=uuid4(),
                plant_profile_id=plant.id,
                water_cost_per_kl=10.0,
                electricity_cost_per_kwh=5.0,
                chitosan_cost_per_kg=300.0,
                calcium_source_type="Ca(OH)2",
                calcium_cost_per_ton=80.0,
                local_brick_market_value=15.0,
                ccts_credit_price=20.0,
            )
            session.add(logistics)
            await session.flush()
            
            # Create 10 users per tenant
            for user_i in range(10):
                user = User(
                    id=uuid4(),
                    organization_id=org.id,
                    email=f"user{user_i}@org{tenant_i}.com",
                    hashed_password=password_service.hash_password("LoadTest123!"),
                    roles=["engineer"],
                    is_active=True,
                )
                session.add(user)
                users.append((user, org, plant.id))
                
        await session.commit()
        return users


@pytest.fixture
def authenticated_users(setup_load_data):
    return setup_load_data


@pytest.fixture
def burst_login_tokens(authenticated_users):
    """Pre-generate 100 login tokens for burst testing to bypass password hashing speed limit."""
    tokens = []
    for user, org, plant_id in authenticated_users:
        token = jwt_service.create_access_token(
            user_id=user.id,
            org_id=org.id,
            roles=user.roles,
            email=user.email,
            mfa_verified=True,
        )
        tokens.append(token)
    return tokens
