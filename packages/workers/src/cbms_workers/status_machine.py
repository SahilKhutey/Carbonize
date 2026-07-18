"""
Report generation status state machine.

States:
  PENDING → GENERATING → AVAILABLE
                       → FAILED
                       → STUCK (timeout, retried by sweep job)

Transitions are atomic (UPDATE ... SET status = ... WHERE status = expected_from).
"""

import enum
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from cbms_shared.logging import get_logger


logger = get_logger(__name__)


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "PENDING"        # Just created, not started
    GENERATING = "GENERATING"   # Worker is processing
    AVAILABLE = "AVAILABLE"     # Successfully generated
    FAILED = "FAILED"           # Permanent failure
    STUCK = "STUCK"             # Timeout, needs recovery


# Valid state transitions
VALID_TRANSITIONS = {
    ReportStatus.PENDING: {ReportStatus.GENERATING, ReportStatus.FAILED, ReportStatus.STUCK},
    ReportStatus.GENERATING: {ReportStatus.AVAILABLE, ReportStatus.FAILED, ReportStatus.STUCK, ReportStatus.PENDING},
    ReportStatus.STUCK: {ReportStatus.GENERATING, ReportStatus.FAILED},
    ReportStatus.AVAILABLE: set(),  # Terminal
    ReportStatus.FAILED: set(),     # Terminal (unless manually retried)
}


class StatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass


class ReportStatusMachine:
    """
    Manages report generation status transitions.
    
    All transitions use optimistic locking:
    UPDATE report SET status = ?, ... WHERE id = ? AND status = ?
    If 0 rows affected, transition failed (someone else changed it).
    """
    
    # Timeout: a GENERATING report is considered STUCK after this
    STUCK_TIMEOUT = timedelta(minutes=5)
    
    @staticmethod
    async def transition(
        db: AsyncSession,
        report_id: str,
        org_id: str,
        from_status: ReportStatus,
        to_status: ReportStatus,
        **extra_fields,
    ) -> bool:
        """
        Attempt to transition a report's status atomically.
        
        Returns True if transition succeeded, False if precondition failed.
        Raises StatusTransitionError if transition is not valid.
        """
        # Validate transition is allowed
        if to_status not in VALID_TRANSITIONS[from_status]:
            raise StatusTransitionError(
                f"Invalid transition: {from_status} → {to_status}"
            )
        
        # Build dynamic SET clause
        set_clauses = ["status = :to_status", "updated_at = :now"]
        params: dict[str, Any] = {
            "to_status": to_status.value,
            "report_id": report_id,
            "org_id": org_id,
            "from_status": from_status.value,
            "now": datetime.now(timezone.utc),
        }
        
        for key, value in extra_fields.items():
            set_clauses.append(f"{key} = :{key}")
            params[key] = value
        
        sql = f"""
            UPDATE generated_reports
            SET {", ".join(set_clauses)}
            WHERE id = :report_id
              AND organization_id = :org_id
              AND status = :from_status
        """
        
        result = await db.execute(text(sql), params)
        
        if result.rowcount == 0:
            # Precondition failed (status was already changed)
            logger.warning(
                "status_transition_failed",
                report_id=report_id,
                from_status=from_status,
                to_status=to_status,
            )
            return False
        
        logger.info(
            "status_transition",
            report_id=report_id,
            from_status=from_status,
            to_status=to_status,
        )
        return True
    
    @staticmethod
    async def claim_for_processing(
        db: AsyncSession,
        report_id: str,
        org_id: str,
        worker_id: str,
    ) -> bool:
        """
        Atomically claim a PENDING or STUCK report for processing.
        
        Returns True if this worker successfully claimed it.
        """
        # We allow claiming from PENDING or STUCK
        # First check current status
        res = await db.execute(
            text("SELECT status FROM generated_reports WHERE id = :report_id AND organization_id = :org_id"),
            {"report_id": report_id, "org_id": org_id}
        )
        row = res.fetchone()
        if not row:
            return False
            
        current_status = ReportStatus(row[0])
        if current_status not in (ReportStatus.PENDING, ReportStatus.STUCK):
            return False
            
        return await ReportStatusMachine.transition(
            db=db,
            report_id=report_id,
            org_id=org_id,
            from_status=current_status,
            to_status=ReportStatus.GENERATING,
            worker_id=worker_id,
            started_at=datetime.now(timezone.utc),
        )
    
    @staticmethod
    async def mark_available(
        db: AsyncSession,
        report_id: str,
        org_id: str,
        s3_key: str,
        file_size_bytes: int,
    ) -> bool:
        """Mark a report as successfully generated."""
        return await ReportStatusMachine.transition(
            db=db,
            report_id=report_id,
            org_id=org_id,
            from_status=ReportStatus.GENERATING,
            to_status=ReportStatus.AVAILABLE,
            s3_key=s3_key,
            file_size_bytes=file_size_bytes,
            completed_at=datetime.now(timezone.utc),
        )
    
    @staticmethod
    async def mark_failed(
        db: AsyncSession,
        report_id: str,
        org_id: str,
        error_message: str,
        permanent: bool = False,
    ) -> bool:
        """Mark a report as failed."""
        return await ReportStatusMachine.transition(
            db=db,
            report_id=report_id,
            org_id=org_id,
            from_status=ReportStatus.GENERATING,
            to_status=ReportStatus.FAILED,
            error_message=error_message,
            failed_at=datetime.now(timezone.utc),
        )
    
    @staticmethod
    async def find_stuck_reports(db: AsyncSession) -> list[dict]:
        """Find reports stuck in GENERATING for too long."""
        from cbms_api.database.models import GeneratedReport
        cutoff = datetime.utcnow() - ReportStatusMachine.STUCK_TIMEOUT
        
        result = await db.execute(
            select(
                GeneratedReport.id,
                GeneratedReport.organization_id,
                GeneratedReport.worker_id,
                GeneratedReport.started_at
            )
            .where(GeneratedReport.status == ReportStatus.GENERATING.value)
            .where(GeneratedReport.started_at < cutoff)
        )
        return [
            {
                "id": row[0],
                "org_id": row[1],
                "worker_id": row[2],
                "started_at": row[3],
            }
            for row in result.fetchall()
        ]
    
    @staticmethod
    async def mark_stuck(db: AsyncSession, report_id: str, org_id: str) -> bool:
        """Mark a stuck report (timeout)."""
        return await ReportStatusMachine.transition(
            db=db,
            report_id=report_id,
            org_id=org_id,
            from_status=ReportStatus.GENERATING,
            to_status=ReportStatus.STUCK,
        )
