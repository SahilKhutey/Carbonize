"""
Integration tests for report generation task.

Verifies:
- Idempotency (running same task_id twice)
- Optimistic locking status transitions
- Atomic S3 uploads
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from unittest.mock import MagicMock, patch

import cbms_api.database.connection as conn_mod
# -----------------------------------------------------------------------------

import pytest_asyncio
from cbms_api.database.models import Base, Organization, SimulationRun, GeneratedReport
from cbms_api.database.connection import async_session_maker

from cbms_workers.storage import storage
from cbms_workers.status_machine import ReportStatusMachine, ReportStatus, StatusTransitionError
from workers.tasks.report import generate_report


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Clean database and setup schema."""
    async with conn_mod.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def seeded_data():
    """Seed base tenant, simulation run and report metadata."""
    async with async_session_maker() as session:
        org = Organization(id=uuid4(), name="Test Org", industry_type="manufacturing")
        session.add(org)
        await session.flush()
        
        sim_run = SimulationRun(
            id=uuid4(),
            organization_id=org.id,
            plant_profile_id=uuid4(),
            status="COMPLETED",
        )
        session.add(sim_run)
        await session.flush()
        
        report = GeneratedReport(
            id=uuid4(),
            organization_id=org.id,
            simulation_run_id=sim_run.id,
            template_id="default_template",
            status=ReportStatus.PENDING.value,
        )
        session.add(report)
        await session.commit()
        
        return org.id, sim_run.id, report.id


class TestReportIdempotency:
    """Task idempotency: same report_id runs produce matching final results."""

    @pytest.mark.anyio
    async def test_running_twice_produces_same_result(self, seeded_data):
        org_id, sim_run_id, report_id = seeded_data
        
        def write_mock_pdf(run, pdf_path):
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4 mock content")

        with patch("workers.tasks.report.generate_pdf_report_file") as mock_gen, \
             patch("cbms_workers.storage.storage.upload_atomic") as mock_upload:
            
            mock_gen.side_effect = write_mock_pdf
            mock_upload.return_value = {"size": 12345}
            
            # First execution
            result1 = generate_report(str(report_id), str(org_id))
            
            # Second execution
            result2 = generate_report(str(report_id), str(org_id))
            
            assert result1["status"] == "available"
            assert result2["status"] == "already_available"
            assert result1["s3_key"] == result2["s3_key"]
            
            # S3 atomic upload should be called exactly once
            mock_upload.assert_called_once()
            mock_gen.assert_called_once()


class TestStatusMachine:
    """State machine transitions are atomic and validated."""

    @pytest.mark.anyio
    async def test_concurrent_workers_only_one_wins(self, seeded_data):
        org_id, _, report_id = seeded_data
        
        async with async_session_maker() as session:
            # Worker 1 and Worker 2 try to claim concurrently
            r1 = await ReportStatusMachine.claim_for_processing(
                db=session,
                report_id=str(report_id),
                org_id=str(org_id),
                worker_id="worker_1",
            )
            r2 = await ReportStatusMachine.claim_for_processing(
                db=session,
                report_id=str(report_id),
                org_id=str(org_id),
                worker_id="worker_2",
            )
            await session.commit()
            
            # Only one worker can claim successfully
            assert (r1 is True and r2 is False) or (r1 is False and r2 is True)

    @pytest.mark.anyio
    async def test_invalid_transition_rejected(self, seeded_data):
        org_id, _, report_id = seeded_data
        
        async with async_session_maker() as session:
            # Claim it first
            await ReportStatusMachine.claim_for_processing(
                db=session,
                report_id=str(report_id),
                org_id=str(org_id),
                worker_id="worker_1",
            )
            # Mark it available
            await ReportStatusMachine.mark_available(
                db=session,
                report_id=str(report_id),
                org_id=str(org_id),
                s3_key="key",
                file_size_bytes=100,
            )
            await session.commit()
            
            # Try invalid transition from AVAILABLE to PENDING
            with pytest.raises(StatusTransitionError):
                await ReportStatusMachine.transition(
                    db=session,
                    report_id=str(report_id),
                    org_id=str(org_id),
                    from_status=ReportStatus.AVAILABLE,
                    to_status=ReportStatus.PENDING,
                )


class TestAtomicS3:
    """S3 atomic upload emulation."""

    @pytest.mark.anyio
    async def test_temp_upload_does_not_replace_final(self):
        # Mock S3 client behavior
        mock_s3_client = MagicMock()
        
        # Simulate exception during copy_object step
        mock_s3_client.copy_object.side_effect = Exception("Copy failed!")
        
        with patch.object(storage, "client", mock_s3_client):
            with pytest.raises(Exception, match="Copy failed!"):
                storage.upload_atomic(
                    content=b"pdf content",
                    final_key="reports/123/report.pdf",
                    on_collision="overwrite",
                )
            
            # Verify temp key was created, then copy failed, and temp was cleaned up
            mock_s3_client.put_object.assert_called_once()
            mock_s3_client.copy_object.assert_called_once()
            # delete_object is called to clean up the temp key
            mock_s3_client.delete_object.assert_called_once()
