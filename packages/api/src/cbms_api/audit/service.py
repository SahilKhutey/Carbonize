"""
Audit logging service.
"""

from cbms_api.database.models import AuditEvent
from cbms_api.database.connection import async_session_maker
from uuid import UUID
from typing import Optional


class AuditService:
    """Service for registering auditable security events in database."""
    
    async def log(
        self,
        org_id: UUID,
        actor_id: str,
        event_type: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log an event to the database."""
        async with async_session_maker() as session:
            from cbms_api.database.connection import set_tenant_context
            await set_tenant_context(session, str(org_id))
            event = AuditEvent(
                organization_id=org_id,
                actor_id=actor_id,
                event_type=event_type,
                ip_address=ip_address
            )
            session.add(event)
            await session.commit()


audit_service = AuditService()
