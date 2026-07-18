"""
Periodic cleanup tasks.

- Recover stuck reports (GENERATING for too long)
- Delete orphaned temp S3 files
- Reap failed reports after retry exhaustion
"""

from datetime import datetime, timezone, timedelta

from cbms_workers.workers.celery_app import celery_app
from cbms_workers.storage import storage
from cbms_workers.status_machine import ReportStatusMachine
from cbms_api.database.connection import async_session_maker
from cbms_shared.logging import get_logger
from cbms_workers.idempotency import run_async_task


logger = get_logger(__name__)


async def recover_stuck_reports_async() -> int:
    """
    Async core of stuck report recovery. Extracted so tests can await
    it directly in the test event loop without spawning a new thread.
    """
    async with async_session_maker() as db:
        stuck = await ReportStatusMachine.find_stuck_reports(db)

    recovered = 0
    for report in stuck:
        async with async_session_maker() as db:
            success = await ReportStatusMachine.mark_stuck(
                db=db,
                report_id=str(report["id"]),
                org_id=str(report["org_id"]),
            )
            if success:
                await db.commit()
                recovered += 1
                logger.info(
                    "stuck_report_recovered",
                    report_id=str(report["id"]),
                    stuck_since=str(report["started_at"]),
                )

    if recovered > 0:
        logger.info("stuck_reports_recovery_complete", count=recovered)

    return recovered


@celery_app.task(name="workers.cleanup.recover_stuck_reports")
def recover_stuck_reports():
    """
    Find reports stuck in GENERATING and mark them as STUCK.

    Runs every 5 minutes. After a report is STUCK, it will be
    automatically retried (up to max_retries).
    """
    return run_async_task(recover_stuck_reports_async())


@celery_app.task(name="workers.cleanup.scrub_orphaned_temp_files")
def scrub_orphaned_temp_files(max_age_hours: int = 24):
    """
    Delete temp S3 files older than max_age_hours.
    
    These can accumulate if a worker died between writing temp
    and copying to final. They are in the `_tmp/` prefix.
    Runs daily.
    """
    import asyncio
    
    async def _scrub():
        # List all _tmp/ files
        paginator = storage.client.get_paginator("list_objects_v2")
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        deleted = 0
        try:
            for page in paginator.paginate(Bucket=storage.bucket, Prefix="_tmp/"):
                contents = page.get("Contents", [])
                for obj in contents:
                    last_modified = obj["LastModified"]
                    # LastModified is timezone-aware
                    if last_modified < cutoff:
                        try:
                            storage.client.delete_object(
                                Bucket=storage.bucket,
                                Key=obj["Key"],
                            )
                            deleted += 1
                        except Exception as e:
                            logger.warning(
                                "orphan_delete_failed",
                                key=obj["Key"],
                                error=str(e),
                            )
        except Exception as e:
            logger.error("error_scrubbing_orphaned_files", error=str(e))
        
        logger.info("orphan_scrub_complete", deleted=deleted)
        return deleted
    
    return run_async_task(_scrub())


@celery_app.task(name="workers.cleanup.periodic_all")
def periodic_cleanup():
    """Run all cleanup tasks."""
    recover_stuck_reports.delay()
    scrub_orphaned_temp_files.delay()
