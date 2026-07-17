"""
Tests for worker death recovery via the sweep/cleanup jobs.
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import cbms_api.database.connection as conn_mod
# -----------------------------------------------------------------------------

import pytest_asyncio
from cbms_api.database.models import Base, Organization, SimulationRun, GeneratedReport
from cbms_api.database.connection import async_session_maker

from cbms_workers.storage import storage
from cbms_workers.status_machine import ReportStatusMachine, ReportStatus
from workers.tasks.cleanup import recover_stuck_reports_async, scrub_orphaned_temp_files
import workers.tasks.cleanup as cleanup_mod

# Ensure the cleanup module uses the test session maker (it imported it at module load)
cleanup_mod.async_session_maker = conn_mod.async_session_maker


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Clean database and setup schema."""
    async with conn_mod.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def stuck_report_data():
    """Seed stuck report data into database."""
    async with async_session_maker() as session:
        org = Organization(id=uuid4(), name="Recovery Org", industry_type="manufacturing")
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
        
        # A report that was started 10 minutes ago
        old_time = datetime.utcnow() - timedelta(minutes=10)
        report = GeneratedReport(
            id=uuid4(),
            organization_id=org.id,
            simulation_run_id=sim_run.id,
            template_id="default_template",
            status=ReportStatus.GENERATING.value,
            started_at=old_time,
        )
        session.add(report)
        await session.commit()
        
        return org.id, report.id


class TestWorkerDeathRecovery:
    """Worker killed mid-task -> recoverable via sweep/cleanup jobs."""

    @pytest.mark.anyio
    async def test_stuck_reports_marked_after_timeout(self, stuck_report_data):
        org_id, report_id = stuck_report_data

        # Call the async core directly in THIS event loop (same SQLite connection)
        count = await recover_stuck_reports_async()

        assert count == 1
        
        # Verify status transitioned to STUCK in the database
        async with async_session_maker() as session:
            report = await session.get(GeneratedReport, report_id)
            assert report.status == ReportStatus.STUCK.value

    @pytest.mark.anyio
    async def test_orphaned_temp_files_cleaned_up(self):
        # Mock S3 list_objects_v2 paginator output
        mock_s3_client = MagicMock()
        mock_paginator = MagicMock()
        
        now = datetime.now(timezone.utc)
        
        # Page contents: one file is fresh (2h), one is orphaned/stale (30h)
        page_contents = {
            "Contents": [
                {"Key": "_tmp/reports/123/fresh.pdf", "LastModified": now - timedelta(hours=2)},
                {"Key": "_tmp/reports/123/orphaned.pdf", "LastModified": now - timedelta(hours=30)},
            ]
        }
        
        mock_paginator.paginate.return_value = [page_contents]
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        with patch.object(storage, "client", mock_s3_client):
            # Run cleanup with 24 hours threshold
            deleted_count = scrub_orphaned_temp_files(max_age_hours=24)
            
            assert deleted_count == 1
            
            # Verify delete was called only on the orphaned/stale file key
            mock_s3_client.delete_object.assert_called_once_with(
                Bucket=storage.bucket,
                Key="_tmp/reports/123/orphaned.pdf",
            )
            
            # Paginator is requested for Prefix _tmp/
            mock_paginator.paginate.assert_called_once_with(
                Bucket=storage.bucket,
                Prefix="_tmp/",
            )
