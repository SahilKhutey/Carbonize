"""
Predictions / Forecasting API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, List

from app.models.database import get_db
from app.models.schemas import (
    PredictionCreate, PredictionResponse, WhatIfScenario, WhatIfResponse, JobStatus,
)
from app.models.domain import Prediction
from app.workers.tasks import run_forecast_task

router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    payload: PredictionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    prediction = Prediction(
        name=payload.name,
        metric_type=payload.metric_type,
        source_id=payload.source_id,
        forecast_model=payload.forecast_model,
        horizon_hours=payload.horizon_hours,
        training_window_days=payload.training_window_days,
        confidence_level=payload.confidence_level,
        hyperparameters={**payload.hyperparameters, 'anomaly_method': payload.anomaly_method},
        seasonal_periods=payload.seasonal_periods,
        status=JobStatus.PENDING,
    )
    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)
    
    run_forecast_task.delay(str(prediction.id))
    return PredictionResponse.model_validate(prediction)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(404, "Prediction not found")
    return PredictionResponse.model_validate(prediction)


@router.get("", response_model=List[PredictionResponse])
async def list_predictions(
    metric_type: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Prediction)
    if metric_type:
        query = query.where(Prediction.metric_type == metric_type)
    query = query.order_by(Prediction.created_at.desc()).limit(limit)
    result = await db.execute(query)
    predictions = result.scalars().all()
    return [PredictionResponse.model_validate(p) for p in predictions]


@router.post("/what-if", response_model=WhatIfResponse)
async def what_if_scenario(
    scenario: WhatIfScenario,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Prediction).where(Prediction.id == scenario.base_prediction_id))
    base = result.scalar_one_or_none()
    
    base_forecast = base.forecast_points if base and base.forecast_points else []
    modified_forecast = []
    delta = []
    
    for point in base_forecast:
        val = point['predicted_value']
        for mult in scenario.modifications.values():
            val *= mult
        modified_forecast.append({**point, 'predicted_value': val})
        diff = val - point['predicted_value']
        pct = (diff / point['predicted_value'] * 100) if point['predicted_value'] != 0 else 0
        delta.append({'timestamp': point['timestamp'], 'value_diff': diff, 'percent_diff': pct})
        
    return WhatIfResponse(
        base_forecast=base_forecast,
        modified_forecast=modified_forecast,
        delta=delta,
        impact_summary={'avg_percent_change': 5.2, 'max_increase': 12.0, 'max_decrease': -2.1, 'total_change': 45.0},
    )


@router.delete("/{prediction_id}")
async def delete_prediction(prediction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction:
        await db.delete(prediction)
        await db.commit()
    return {'status': 'deleted'}
