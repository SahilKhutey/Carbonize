"""
Test run endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.models.database import get_db
from app.models.schemas import TestRunCreate, TestRunResponse, JobStatus
from app.models.domain import TestRun, TestPrediction as TestPredictionDB
from app.workers.tasks import run_batch_inference_task

router = APIRouter(prefix="/v1/tests", tags=["tests"])


@router.post("/runs", response_model=TestRunResponse, status_code=201)
async def create_test_run(
    payload: TestRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    test_run = TestRun(
        name=payload.name,
        description=payload.description,
        model_id=payload.model_id,
        model_version="1.5.0",
        test_type=payload.test_type.value,
        dataset_id=payload.dataset_id,
        config=payload.config,
        comparison_model_id=payload.comparison_model_id,
        status=JobStatus.PENDING,
    )
    db.add(test_run)
    await db.commit()
    await db.refresh(test_run)
    
    run_batch_inference_task.delay(str(test_run.id))
    return TestRunResponse.model_validate(test_run)


@router.get("/runs/{run_id}", response_model=TestRunResponse)
async def get_test_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestRun).where(TestRun.id == run_id))
    test_run = result.scalar_one_or_none()
    if not test_run:
        raise HTTPException(404, "Test run not found")
    return TestRunResponse.model_validate(test_run)


@router.get("/runs/{run_id}/predictions")
async def get_test_predictions(
    run_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TestPredictionDB).where(TestPredictionDB.test_run_id == run_id).limit(limit))
    return result.scalars().all()


@router.post("/runs/{run_id}/cancel")
async def cancel_test_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestRun).where(TestRun.id == run_id))
    test_run = result.scalar_one_or_none()
    if test_run:
        test_run.status = JobStatus.CANCELLED
        await db.commit()
    return {'status': 'cancelled'}


@router.post("/ab-test")
async def create_ab_test(
    model_a_id: UUID,
    model_b_id: UUID,
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    test_run = TestRun(
        name=f"A/B Test",
        model_id=model_a_id,
        test_type="ab_test",
        dataset_id=dataset_id,
        comparison_model_id=model_b_id,
        status=JobStatus.PENDING,
    )
    db.add(test_run)
    await db.commit()
    await db.refresh(test_run)
    run_batch_inference_task.delay(str(test_run.id))
    return {'test_run_id': test_run.id, 'status': 'queued'}


@router.post("/tuning")
async def start_tuning(
    model_id: UUID,
    search_space: Dict[str, Any],
    trials: int = 20,
    db: AsyncSession = Depends(get_db),
):
    test_run = TestRun(
        name=f"Hyperparameter Tuning",
        model_id=model_id,
        test_type="regression",
        config={'tuning': True, 'search_space': search_space, 'trials': trials},
        status=JobStatus.PENDING,
    )
    db.add(test_run)
    await db.commit()
    await db.refresh(test_run)
    return {'tuning_id': test_run.id, 'trials': trials}
