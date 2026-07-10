"""
api/dependencies.py
Dependencies for routing, including async database sessions and auth/context helper.
"""

from typing import AsyncGenerator, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Header
from database.connection import get_db_session
from database.models import Organization

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to retrieve the async SQLAlchemy database session."""
    async for session in get_db_session():
        yield session

async def get_active_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
) -> UUID:
    """
    Retrieves the tenant organization context from request headers.
    Falls back to a default organization if the header is omitted.
    """
    if x_tenant_id:
        try:
            return UUID(x_tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Tenant-ID header. Must be a valid UUID v4."
            )

    result = await db.execute(select(Organization).limit(1))
    org = result.scalars().first()
    
    if not org:
        org = Organization(
            name="CarbonLattice Operations India",
            industry_type="power_generation"
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
        
    return org.id
