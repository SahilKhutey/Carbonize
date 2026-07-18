"""
api/dependencies.py
Dependencies for routing, including async database sessions and auth/context helper.
"""

from typing import AsyncGenerator, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Header
from cbms_api.database.connection import get_db_session
from cbms_api.database.models import Organization

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to retrieve the async SQLAlchemy database session."""
    async for session in get_db_session():
        yield session

from cbms_api.auth.rbac import get_current_active_user, AuthUser


async def get_active_tenant_id(
    user: AuthUser = Depends(get_current_active_user)
) -> UUID:
    """
    Retrieves the tenant organization context from the authenticated user context.
    """
    return user.org_id

