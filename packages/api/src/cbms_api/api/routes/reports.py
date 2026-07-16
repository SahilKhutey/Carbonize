"""
api/routes/reports.py
Endpoints to fetch and compile PDF reports for simulation runs.
"""

import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_active_tenant_id
from database.models import SimulationRun, PlantProfile
from workers.report_generator import generate_pdf_report_file
from cbms_api.middleware.rate_limiting import rate_limit_expensive

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{run_id}", response_class=FileResponse)
@rate_limit_expensive(limit="5/minute;50/hour")
async def get_pdf_report(
    request: Request,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Retrieves the generated PDF report. Generates it dynamically if it doesn't exist yet.
    """
    result = await db.execute(
        select(SimulationRun)
        .options(
            selectinload(SimulationRun.result),
            selectinload(SimulationRun.plant).selectinload(PlantProfile.logistics)
        )
        .filter(SimulationRun.id == run_id)
        .filter(SimulationRun.organization_id == org_id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation run not found or access denied."
        )
        
    if run.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot generate report for run in status: {run.status}."
        )

    # Output directory for compiled PDFs
    pdf_dir = os.path.abspath("reports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"report_{run.id}.pdf")

    # Generate the file if not already on disk
    if not os.path.exists(pdf_path):
        try:
            generate_pdf_report_file(run, pdf_path)
            run.pdf_report_url = f"/reports/download/{run.id}"
            await db.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to compile PDF report: {str(e)}"
            )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"CarbonLattice_Report_{run.id}.pdf"
    )
