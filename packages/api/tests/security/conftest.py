"""
Test fixtures for multi-tenant data isolation tests.
"""

import pytest
import asyncio
import secrets
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta

# -----------------------------------------------------------------------------
# MONKEYPATCH BCRYPT AND DATABASE FOR IN-MEMORY SQLITE TESTING
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
import database.connection as conn_mod_alt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

sqlite_test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
sqlite_sessionmaker = async_sessionmaker(
    bind=sqlite_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

conn_mod.engine = sqlite_test_engine
conn_mod.async_session_maker = sqlite_sessionmaker
conn_mod_alt.engine = sqlite_test_engine
conn_mod_alt.async_session_maker = sqlite_sessionmaker
# -----------------------------------------------------------------------------

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from cbms_api.api.main import app
from cbms_api.config import get_settings
from cbms_api.database.models import (
    Base, Organization, User, PlantProfile, LogisticsConfig,
    SimulationRun, SimulationResult, AuditEvent
)
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


async def create_tenant_with_data(
    session: AsyncSession,
    org_name: str = "Test Org",
    user_email: str = "user@example.com",
) -> tuple[Organization, User, dict]:
    """
    Create a complete tenant with realistic data.
    """
    # Create organization
    org = Organization(
        id=uuid4(),
        name=org_name,
        industry_type="Cement",
    )
    session.add(org)
    await session.flush()
    
    # Create user
    user = User(
        id=uuid4(),
        organization_id=org.id,
        email=user_email,
        hashed_password=password_service.hash_password("SuperSecret!123"),
        roles=["engineer"],
        is_active=True,
    )
    session.add(user)
    await session.flush()
    
    # Create plant
    plant = PlantProfile(
        id=uuid4(),
        organization_id=org.id,
        name=f"{org_name} Plant",
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
    
    # Create logistics config
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
    
    # Create simulation run
    sim_run = SimulationRun(
        id=uuid4(),
        organization_id=org.id,
        plant_profile_id=plant.id,
        status="COMPLETED",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        input_hash=secrets.token_hex(16),
    )
    session.add(sim_run)
    await session.flush()
    
    # Create simulation result
    sim_result = SimulationResult(
        id=uuid4(),
        simulation_run_id=sim_run.id,
        co2_capture_efficiency_pct=87.2,
        so2_capture_efficiency_pct=96.5,
        predicted_block_strength_mpa=24.0,
        block_grade="Grade A",
        hourly_block_yield_kg=500.0,
        annual_block_count=10000,
        estimated_opex_per_ton_co2=50.0,
        annual_ccts_revenue_inr=1000000.0,
        annual_block_revenue_inr=500000.0,
        annual_opex_inr=800000.0,
        annual_net_revenue_inr=700000.0,
        capex_total_inr=5000000.0,
        simple_payback_months=36.0,
        npv_10yr_inr=80000000.0,
        irr_pct=25.0,
        mean_saturation_time_hours=4.0,
        p95_saturation_time_hours=6.0,
        cpcb_compliant=True,
    )
    session.add(sim_result)
    await session.flush()
    
    # Create audit event
    audit = AuditEvent(
        id=uuid4(),
        organization_id=org.id,
        actor_id=str(user.id),
        event_type="test.audit",
    )
    session.add(audit)
    await session.commit()
    
    resource_ids = {
        "plant": plant.id,
        "simulation": sim_run.id,
        "result": sim_result.id,
        "audit": audit.id,
    }
    
    return org, user, resource_ids


@pytest_asyncio.fixture
async def setup_test_data():
    """Ensure clean table structures and seed two independent tenants."""
    async with conn_mod.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session_maker() as session:
        # Tenant A
        org_a, user_a, ids_a = await create_tenant_with_data(
            session, org_name="Tenant A", user_email="alice@tenanta.com"
        )
        # Tenant B
        org_b, user_b, ids_b = await create_tenant_with_data(
            session, org_name="Tenant B", user_email="bob@tenantb.com"
        )
        
        return {
            "tenant_a": (org_a, user_a, ids_a),
            "tenant_b": (org_b, user_b, ids_b),
        }


@pytest.fixture
def tenant_a(setup_test_data):
    return setup_test_data["tenant_a"]


@pytest.fixture
def tenant_b(setup_test_data):
    return setup_test_data["tenant_b"]


@pytest.fixture
def auth_a(tenant_a):
    org_a, user_a, _ = tenant_a
    token = jwt_service.create_access_token(
        user_id=user_a.id,
        org_id=org_a.id,
        roles=user_a.roles,
        email=user_a.email,
        mfa_verified=True,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_b(tenant_b):
    org_b, user_b, _ = tenant_b
    token = jwt_service.create_access_token(
        user_id=user_b.id,
        org_id=org_b.id,
        roles=user_b.roles,
        email=user_b.email,
        mfa_verified=True,
    )
    return {"Authorization": f"Bearer {token}"}
