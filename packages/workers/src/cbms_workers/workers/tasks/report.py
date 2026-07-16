"""
Report generation Celery task — IDEMPOTENT + ATOMIC + RETRY-SAFE.

Key properties:
1. Idempotent: Same task_id (i.e., same report_id) run twice produces
   the same final result and never overwrites with a partial result.
2. Atomic: Either the report is fully generated and available,
   or it's marked FAILED with cleanup. Never half-done.
3. Retry-safe: Transient failures retry with exponential backoff.
   Worker death is detected and recovered by the sweep job.
4. State-tracked: Every transition is atomic in the database.
"""

import os
import tempfile
from datetime import datetime, timezone
from uuid import UUID

from celery.exceptions import SoftTimeLimitExceeded

from workers.celery_app import celery_app
from cbms_workers.storage import storage
from cbms_workers.status_machine import ReportStatusMachine, ReportStatus
from cbms_workers.retry import report_retry_policy, RETRYABLE_EXCEPTIONS
from cbms_workers.idempotency import idempotent_task, run_async_task

from database.connection import async_session_maker
from database.models import SimulationRun, GeneratedReport
from workers.report_generator import generate_pdf_report_file
from cbms_shared.logging import get_logger


logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="workers.reports.generate",
    queue="reporting",
    max_retries=3,
    default_retry_delay=10,        # 10s initial delay (exponential with backoff)
    time_limit=600,                # 10 min hard limit
    soft_time_limit=540,           # 9 min soft limit (raises SoftTimeLimitExceeded)
    acks_late=True,                 # Don't requeue if worker dies after ack
)
def generate_report(
    self,
    report_id: str,
    org_id: str,
    worker_id: str = None,
):
    """
    Generate a PDF report and upload to S3.
    
    IDEMPOTENT: This task can be safely retried (same report_id → same result).
    ATOMIC: The S3 file is only updated after complete generation.
    
    Args:
        report_id: The GeneratedReport UUID (also the Celery task ID)
        org_id: Organization ID (for RLS context)
        worker_id: ID of the worker processing this task
    """
    worker_id = worker_id or self.request.id or "unknown_worker"
    logger.info(
        "report_generation_started",
        report_id=report_id,
        org_id=org_id,
        worker_id=worker_id,
        attempt=self.request.retries + 1,
    )
    
    async def _process():
        # Step 1: Check and claim processing status atomically
        async with async_session_maker() as db:
            current = await db.get(GeneratedReport, UUID(report_id))
            if current is None:
                raise ValueError(f"Report {report_id} not found")
            
            if current.status == ReportStatus.AVAILABLE.value:
                logger.info("report_already_available", report_id=report_id)
                return {"status": "already_available", "s3_key": current.s3_key}
            
            # Try to claim (PENDING or STUCK → GENERATING)
            claimed = await ReportStatusMachine.claim_for_processing(
                db=db,
                report_id=report_id,
                org_id=org_id,
                worker_id=worker_id,
            )
            if not claimed:
                logger.info("report_already_claimed", report_id=report_id)
                return {"status": "already_processing"}
            
            # Get associated simulation run for details
            run = await db.get(SimulationRun, current.simulation_run_id)
            if run is None:
                raise ValueError(f"Simulation run {current.simulation_run_id} not found")
                
            await db.commit()

        # Step 2: Generate report content wrapped in retry logic
        try:
            content, s3_key, content_type = _generate_content_wrapper(run, org_id, report_id)
        except SoftTimeLimitExceeded:
            logger.warning("report_generation_timeout", report_id=report_id)
            raise
        except RETRYABLE_EXCEPTIONS as e:
            logger.warning("report_generation_transient_error", report_id=report_id, error=str(e))
            # Mark back to PENDING/STUCK for retry
            async with async_session_maker() as db:
                await ReportStatusMachine.transition(
                    db=db, report_id=report_id, org_id=org_id,
                    from_status=ReportStatus.GENERATING,
                    to_status=ReportStatus.PENDING,
                )
                await db.commit()
            raise self.retry(exc=e, countdown=10)
        except Exception as e:
            logger.exception("report_generation_failed", report_id=report_id)
            async with async_session_maker() as db:
                await ReportStatusMachine.mark_failed(
                    db=db, report_id=report_id, org_id=org_id,
                    error_message=str(e)[:500], permanent=True,
                )
                await db.commit()
            raise

        # Step 3: Atomic upload to S3 (temp -> copy -> delete temp)
        try:
            result = storage.upload_atomic(
                content=content,
                final_key=s3_key,
                content_type=content_type,
                metadata={
                    "report_id": report_id,
                    "org_id": org_id,
                    "generated_by": worker_id,
                },
            )
        except Exception as e:
            logger.exception("report_upload_failed", report_id=report_id)
            async with async_session_maker() as db:
                await ReportStatusMachine.mark_failed(
                    db=db, report_id=report_id, org_id=org_id,
                    error_message=f"Upload failed: {str(e)[:500]}", permanent=True,
                )
                await db.commit()
            raise

        # Step 4: Mark available
        async with async_session_maker() as db:
            success = await ReportStatusMachine.mark_available(
                db=db,
                report_id=report_id,
                org_id=org_id,
                s3_key=s3_key,
                file_size_bytes=result["size"],
            )
            await db.commit()
            
        logger.info(
            "report_generation_complete",
            report_id=report_id,
            s3_key=s3_key,
            size_bytes=result["size"],
        )
        return {
            "status": "available",
            "s3_key": s3_key,
            "size": result["size"],
        }

    return run_async_task(_process())


@report_retry_policy(max_attempts=3, initial_delay_s=2.0)
def _generate_content_wrapper(run: SimulationRun, org_id: str, report_id: str) -> tuple[bytes, str, str]:
    """Generates PDF/HTML content from simulation run with retries on transient errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "report.pdf")
        generate_pdf_report_file(run, pdf_path)
        
        # Check if PDF or HTML fallback was generated
        final_path = pdf_path
        if not os.path.exists(pdf_path):
            html_path = pdf_path.replace(".pdf", ".html")
            if os.path.exists(html_path):
                final_path = html_path
                s3_key = f"reports/{org_id}/{report_id}.html"
                content_type = "text/html"
            else:
                raise FileNotFoundError("No report file was generated by the report generator")
        else:
            s3_key = f"reports/{org_id}/{report_id}.pdf"
            content_type = "application/pdf"
            
        with open(final_path, "rb") as f:
            content = f.read()
            
        return content, s3_key, content_type
