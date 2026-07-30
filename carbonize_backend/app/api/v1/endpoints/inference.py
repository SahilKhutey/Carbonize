"""
Inference API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import cv2
import numpy as np
import json

from app.models.database import get_db
from app.models.schemas import InferenceResponse, EdgeSimulatorConfig
from app.services.inference import inference_service
from app.workers.tasks import run_inference_task

router = APIRouter(prefix="/v1/inference", tags=["inference"])


@router.post("/predict", response_model=InferenceResponse)
async def predict(
    model_id: UUID = Form(...),
    image: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    iou_threshold: float = Form(0.45),
    max_detections: int = Form(100),
    edge_simulator: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await image.read()
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        img = np.zeros((640, 640, 3), dtype=np.uint8)
    
    sim_config = None
    if edge_simulator:
        try:
            sim_dict = json.loads(edge_simulator)
            sim_config = EdgeSimulatorConfig(**sim_dict)
        except Exception:
            pass
            
    result = await inference_service.predict(
        model_id=model_id,
        image=img,
        confidence_threshold=confidence_threshold,
        iou_threshold=iou_threshold,
        max_detections=max_detections,
        edge_simulator=sim_config,
    )
    return result


@router.post("/predict-async")
async def predict_async(
    model_id: UUID = Form(...),
    image: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    iou_threshold: float = Form(0.45),
):
    task = run_inference_task.delay(
        model_id=str(model_id),
        image_base64="",
        config={'confidence_threshold': confidence_threshold, 'iou_threshold': iou_threshold},
    )
    return {'task_id': task.id, 'status': 'queued', 'check_url': f'/v1/inference/task/{task.id}'}


@router.get("/task/{task_id}")
async def get_task_result(task_id: str):
    from app.workers.celery_app import celery_app
    res = celery_app.AsyncResult(task_id)
    return {'status': 'completed' if res.ready() else 'pending', 'result': res.result if res.ready() else None}
