import os
import json
import hashlib
import asyncio
import redis.asyncio as async_redis
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from cbms_api.api.dependencies import get_db, get_active_tenant_id
from cbms_api.database.models import PlantProfile, SimulationRun, SimulationResult
from cbms_api.schemas.simulation import SimulationCreateRequest
from cbms_api.middleware.rate_limiting import rate_limit_expensive, rate_limit_read, rate_limit_write

router = APIRouter(prefix="/simulations", tags=["Simulations"])
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

def generate_input_hash(
    plant_profile_id: str,
    press_force_bar: float,
    enzyme_concentration_mg_l: float,
    chitosan_wt_pct: float,
    reactor_temperature_c: float
) -> str:
    raw_str = f"{plant_profile_id}-{press_force_bar:.1f}-{enzyme_concentration_mg_l:.1f}-{chitosan_wt_pct:.1f}-{reactor_temperature_c:.1f}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

@router.post("", response_model=None, status_code=status.HTTP_202_ACCEPTED)
@rate_limit_expensive(limit="10/minute;100/hour")
async def trigger_simulation(
    request: Request,
    schema: SimulationCreateRequest,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Creates a SimulationRun record and dispatches a background Celery worker task.
    Supports cache checks for identical parameters.
    """
    # Verify plant profile exists and belongs to the current tenant
    plant_result = await db.execute(
        select(PlantProfile)
        .filter(PlantProfile.id == UUID(schema.plant_profile_id))
        .filter(PlantProfile.organization_id == org_id)
    )
    plant = plant_result.scalars().first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced plant profile not found or access denied."
        )

    # Compute input hash
    h = generate_input_hash(
        schema.plant_profile_id,
        schema.press_force_bar,
        schema.enzyme_concentration_mg_l,
        schema.chitosan_wt_pct,
        schema.reactor_temperature_c
    )

    # Check for completed runs with matching input hash
    cached_run_result = await db.execute(
        select(SimulationRun)
        .options(selectinload(SimulationRun.result))
        .filter(SimulationRun.organization_id == org_id)
        .filter(SimulationRun.input_hash == h)
        .filter(SimulationRun.status == "COMPLETED")
    )
    cached_run = cached_run_result.scalars().first()

    if cached_run and cached_run.result:
        # Create a new run record marked as COMPLETED instantly
        run = SimulationRun(
            organization_id=org_id,
            plant_profile_id=plant.id,
            status="COMPLETED",
            press_force_bar=schema.press_force_bar,
            enzyme_concentration_mg_l=schema.enzyme_concentration_mg_l,
            chitosan_wt_pct=schema.chitosan_wt_pct,
            input_hash=h,
            pdf_report_url=cached_run.pdf_report_url
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Clone the results
        orig_res = cached_run.result
        res = SimulationResult(
            simulation_run_id=run.id,
            co2_capture_efficiency_pct=orig_res.co2_capture_efficiency_pct,
            so2_capture_efficiency_pct=orig_res.so2_capture_efficiency_pct,
            predicted_block_strength_mpa=orig_res.predicted_block_strength_mpa,
            block_grade=orig_res.block_grade,
            hourly_block_yield_kg=orig_res.hourly_block_yield_kg,
            annual_block_count=orig_res.annual_block_count,
            estimated_opex_per_ton_co2=orig_res.estimated_opex_per_ton_co2,
            annual_ccts_revenue_inr=orig_res.annual_ccts_revenue_inr,
            annual_block_revenue_inr=orig_res.annual_block_revenue_inr,
            annual_opex_inr=orig_res.annual_opex_inr,
            annual_net_revenue_inr=orig_res.annual_net_revenue_inr,
            capex_total_inr=orig_res.capex_total_inr,
            simple_payback_months=orig_res.simple_payback_months,
            npv_10yr_inr=orig_res.npv_10yr_inr,
            irr_pct=orig_res.irr_pct,
            mean_saturation_time_hours=orig_res.mean_saturation_time_hours,
            p95_saturation_time_hours=orig_res.p95_saturation_time_hours,
            cpcb_compliant=orig_res.cpcb_compliant,
            uq_metrics=orig_res.uq_metrics
        )
        db.add(res)
        await db.commit()
        await db.refresh(run)

        # Publish completion event
        try:
            from cbms_workers.workers.tasks import publish_progress
            publish_progress(str(run.id), "COMPLETED", 100, 100, "Simulation completed instantly via cache lookup.")
        except Exception:
            pass

        return run

    # Initialize a new run record
    run = SimulationRun(
        organization_id=org_id,
        plant_profile_id=plant.id,
        status="PENDING",
        press_force_bar=schema.press_force_bar,
        enzyme_concentration_mg_l=schema.enzyme_concentration_mg_l,
        chitosan_wt_pct=schema.chitosan_wt_pct,
        input_hash=h
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Dispatch to background Celery worker
    task_id = None
    try:
        from cbms_workers.workers.tasks import run_simulation_task
        async_res = run_simulation_task.delay(
            str(run.id),
            schema.reactor_temperature_c,
            schema.override_co2_efficiency,
            schema.override_so2_efficiency
        )
        task_id = async_res.id
    except Exception:
        pass

    if task_id:
        run.celery_task_id = task_id
        await db.commit()
        await db.refresh(run)

    return run

@router.get("/{run_id}", response_model=None)
@rate_limit_read(limit="300/minute")
async def get_simulation_status(
    request: Request,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Polls the current status and results of a simulation run under tenant scope.
    """
    result = await db.execute(
        select(SimulationRun)
        .options(selectinload(SimulationRun.result))
        .filter(SimulationRun.id == run_id)
        .filter(SimulationRun.organization_id == org_id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation run not found or access denied."
        )
    return run

@router.delete("/{run_id}/cancel", status_code=status.HTTP_200_OK)
@rate_limit_expensive(limit="30/minute")
async def cancel_simulation(
    request: Request,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Manually revokes and cancels an active simulation run task.
    """
    result = await db.execute(
        select(SimulationRun)
        .filter(SimulationRun.id == run_id)
        .filter(SimulationRun.organization_id == org_id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation run not found or access denied."
        )

    if run.status in ("COMPLETED", "FAILED", "CANCELLED"):
        return {"status": run.status, "message": "Simulation is already in a terminal state."}

    # Revoke Celery task
    if run.celery_task_id:
        try:
            from cbms_workers.workers.celery_app import celery_app
            celery_app.control.revoke(run.celery_task_id, terminate=True)
        except Exception:
            pass

    run.status = "CANCELLED"
    await db.commit()

    # Publish cancellation status
    try:
        from cbms_workers.workers.tasks import publish_progress
        publish_progress(str(run.id), "CANCELLED", 100, 100, "Simulation manually cancelled by user")
    except Exception:
        pass

    return {"status": "CANCELLED", "message": "Simulation run cancelled and worker task revoked."}

@router.websocket("/{run_id}/stream")
async def stream_simulation_progress(
    websocket: WebSocket,
    run_id: UUID
):
    """
    WebSocket endpoint that streams real-time simulation progress from Redis pub/sub.
    """
    await websocket.accept()

    try:
        r_client = async_redis.Redis.from_url(REDIS_URL)
        pubsub = r_client.pubsub()
        await pubsub.subscribe(f"simulation.{run_id}.progress")
    except Exception as e:
        await websocket.send_json({"error": f"Failed to connect to event stream: {str(e)}"})
        await websocket.close()
        return

    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg.get("type") == "message":
                data = msg["data"].decode("utf-8") if isinstance(msg["data"], bytes) else msg["data"]
                await websocket.send_text(data)
                
                # Check for terminal state payload
                payload = json.loads(data)
                if payload.get("stage") in ("COMPLETED", "FAILED", "CANCELLED"):
                    break
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe()
        await pubsub.close()
        await r_client.close()
