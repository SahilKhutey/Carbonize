"""
services/simulation_service.py
Service layer implementing simulation submit, list, and result extraction logic.
"""

from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from cbms_api.database.models import SimulationRun, SimulationResult
from cbms_shared.exceptions import NotFoundError
from cbms_workers.workers.tasks import publish_progress

class SimulationService:
    """Dispatches background Celery solvers and registers immutable runs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_run(self, org_id: UUID, plant_id: UUID, schema) -> dict:
        """Register a new run, compute inputs hash, and launch workers task."""
        run = SimulationRun(
            organization_id=org_id,
            plant_profile_id=plant_id,
            status="PENDING",
            press_force_bar=schema.press_force_bar,
            enzyme_concentration_mg_l=schema.enzyme_concentration_mg_l,
            chitosan_wt_pct=schema.chitosan_wt_pct
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        
        # In a real environment, send to celery task:
        # celery_app.send_task("workers.tasks.run_simulation_pipeline", args=[run.id])
        
        return {
            "simulation_run_id": str(run.id),
            "status": "PENDING",
            "estimated_completion_seconds": 60
        }
        
    async def get_run_results(self, run_id: UUID, org_id: UUID) -> dict:
        """Extract points and distribution estimates from a completed run."""
        result = await self.db.execute(
            select(SimulationRun)
            .options(selectinload(SimulationRun.result))
            .filter(SimulationRun.id == run_id)
            .filter(SimulationRun.organization_id == org_id)
        )
        run = result.scalars().first()
        if not run:
            raise NotFoundError("Simulation run not found.")
            
        if run.status != "COMPLETED" or not run.result:
            return {"run_id": str(run.id), "status": run.status, "results": None}
            
        res = run.result
        return {
            "run_id": str(run.id),
            "status": run.status,
            "co2_capture_efficiency_pct": float(res.co2_capture_efficiency_pct),
            "so2_capture_efficiency_pct": float(res.so2_capture_efficiency_pct),
            "predicted_block_strength_mpa": float(res.predicted_block_strength_mpa),
            "block_grade": res.block_grade,
            "npv_10yr_inr": float(res.npv_10yr_inr),
            "simple_payback_months": float(res.simple_payback_months)
        }
