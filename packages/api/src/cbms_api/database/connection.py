"""
database/connection.py
Database connection configuration and session management for async SQLAlchemy.
"""

import os
import logging

logger = logging.getLogger(__name__)
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# PostgreSQL Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/biomimetic_db"
)

# Engine setup with pre-ping validation
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Async session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

from fastapi import Request
from sqlalchemy import text


async def get_db_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for obtaining an async session.
    Automatically applies PostgreSQL RLS tenant context if request is authenticated.
    """
    async with async_session_maker() as session:
        org_id = None
        if request is not None:
            org_id = getattr(request.state, "org_id", None)
            
        if org_id is not None and "sqlite" not in str(session.bind.url):
            await session.execute(
                text(f"SET LOCAL app.current_org_id = '{org_id}'")
            )
            
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def set_tenant_context(session: AsyncSession, org_id: str) -> None:
    """Manually configure tenant context on session connection."""
    if "sqlite" not in str(session.bind.url):
        await session.execute(
            text(f"SET LOCAL app.current_org_id = '{org_id}'")
        )


async def init_database_rls() -> None:
    """
    Initialize PostgreSQL Row-Level Security policies on all tenant tables.
    """
    if "sqlite" in str(engine.url):
        logger.info("Skipping RLS setup for SQLite database engine")
        return
        
    statements = [
        # plant_profiles
        "ALTER TABLE plant_profiles ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE plant_profiles FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS plant_profiles_isolation ON plant_profiles;",
        """CREATE POLICY plant_profiles_isolation ON plant_profiles
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",

        # simulation_runs
        "ALTER TABLE simulation_runs ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE simulation_runs FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS simulation_runs_isolation ON simulation_runs;",
        """CREATE POLICY simulation_runs_isolation ON simulation_runs
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",

        # logistics_configs
        "ALTER TABLE logistics_configs ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE logistics_configs FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS logistics_configs_isolation ON logistics_configs;",
        """CREATE POLICY logistics_configs_isolation ON logistics_configs
            USING (EXISTS (
                SELECT 1 FROM plant_profiles
                WHERE plant_profiles.id = logistics_configs.plant_profile_id
                  AND plant_profiles.organization_id = current_setting('app.current_org_id', TRUE)::UUID
            ))
            WITH CHECK (EXISTS (
                SELECT 1 FROM plant_profiles
                WHERE plant_profiles.id = logistics_configs.plant_profile_id
                  AND plant_profiles.organization_id = current_setting('app.current_org_id', TRUE)::UUID
            ));""",

        # simulation_results
        "ALTER TABLE simulation_results ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE simulation_results FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS simulation_results_isolation ON simulation_results;",
        """CREATE POLICY simulation_results_isolation ON simulation_results
            USING (EXISTS (
                SELECT 1 FROM simulation_runs
                WHERE simulation_runs.id = simulation_results.simulation_run_id
                  AND simulation_runs.organization_id = current_setting('app.current_org_id', TRUE)::UUID
            ))
            WITH CHECK (EXISTS (
                SELECT 1 FROM simulation_runs
                WHERE simulation_runs.id = simulation_results.simulation_run_id
                  AND simulation_runs.organization_id = current_setting('app.current_org_id', TRUE)::UUID
            ));""",

        # users
        "ALTER TABLE users ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE users FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS users_isolation ON users;",
        """CREATE POLICY users_isolation ON users
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",

        # refresh_tokens
        "ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE refresh_tokens FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS refresh_tokens_isolation ON refresh_tokens;",
        """CREATE POLICY refresh_tokens_isolation ON refresh_tokens
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",

        # audit_events
        "ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS audit_events_isolation ON audit_events;",
        """CREATE POLICY audit_events_isolation ON audit_events
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",

        # generated_reports
        "ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE generated_reports FORCE ROW LEVEL SECURITY;",
        "DROP POLICY IF EXISTS generated_reports_isolation ON generated_reports;",
        """CREATE POLICY generated_reports_isolation ON generated_reports
            USING (organization_id = current_setting('app.current_org_id', TRUE)::UUID)
            WITH CHECK (organization_id = current_setting('app.current_org_id', TRUE)::UUID);""",
    ]
    
    async with engine.begin() as conn:
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                # Ignore failures if table doesn't exist yet during initial metadata creation
                logger.warning(f"Failed to execute RLS setup statement: {stmt}. Error: {e}")



