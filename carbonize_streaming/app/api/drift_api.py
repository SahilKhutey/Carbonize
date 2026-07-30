"""
Drift detection API endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
import numpy as np

from app.drift.drift_detector import MultiMethodDriftDetector, ConceptDriftDetector
from app.processors.drift_processor import drift_processor

router = APIRouter(prefix="/v1/drift", tags=["drift"])


class DriftDetectionRequest(BaseModel):
    reference_data: Dict[str, List[float]]
    test_data: Dict[str, List[float]]
    methods: Optional[List[str]] = ['ks_test', 'psi', 'js_divergence']


class ResetRequest(BaseModel):
    metric_key: str


@router.post("/detect")
async def detect_drift(req: DriftDetectionRequest):
    detector = MultiMethodDriftDetector({'methods': req.methods, 'thresholds': {'ks_test': 0.05, 'psi': 0.25, 'js_divergence': 0.1}, 'min_methods_drifted': 2, 'min_samples': 10})
    ref_data = {k: np.array(v) for k, v in req.reference_data.items()}
    test_data = {k: np.array(v) for k, v in req.test_data.items()}
    summary = detector.detect(test_data, ref_data)
    return summary


@router.get("/state")
async def get_drift_state():
    return drift_processor.get_all_states()


@router.post("/reset")
async def reset_drift_detector(req: ResetRequest):
    if req.metric_key in drift_processor._detectors:
        drift_processor._detectors[req.metric_key].reset()
        return {'status': 'reset', 'metric_key': req.metric_key}
    return {'status': 'ok', 'metric_key': req.metric_key}
