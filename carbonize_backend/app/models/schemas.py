"""
Pydantic schemas for API request/response
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class ModelStage(str, Enum):
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class ModelFormat(str, Enum):
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    TFLITE = "tflite"


class TestType(str, Enum):
    SINGLE = "single"
    BATCH = "batch"
    AB_TEST = "ab_test"
    REGRESSION = "regression"
    STRESS = "stress"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float = Field(ge=0, le=1)
    class_id: int = Field(ge=0)
    class_name: str


class DetectionResult(BaseModel):
    bbox: BoundingBox
    mask: Optional[List[List[float]]] = None
    keypoints: Optional[List[List[float]]] = None


class InferenceResponse(BaseModel):
    request_id: str
    model_version: str
    detections: List[BoundingBox]
    inference_time_ms: float
    preprocessing_ms: float
    postprocessing_ms: float
    image_dimensions: Dict[str, int]
    metadata: Optional[Dict[str, Any]] = None


class TestRunCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_id: UUID
    test_type: TestType
    dataset_id: Optional[UUID] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    comparison_model_id: Optional[UUID] = None
    
    @field_validator('config')
    @classmethod
    def validate_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        allowed_keys = {'confidence_threshold', 'iou_threshold', 'max_detections', 'batch_size', 'edge_simulator', 'run_comparison', 'tuning', 'search_space', 'trials'}
        invalid = set(v.keys()) - allowed_keys
        if invalid:
            raise ValueError(f"Invalid config keys: {invalid}")
        return v


class TestRunResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    model_id: UUID
    model_version: Optional[str] = None
    test_type: str
    status: JobStatus
    progress: float
    total_samples: int
    processed_samples: int
    failed_samples: int
    metrics: Dict[str, Any] = Field(default_factory=dict)
    per_class_metrics: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TestPrediction(BaseModel):
    sample_id: str
    image_url: Optional[str] = None
    ground_truth: Optional[List[BoundingBox]] = None
    predictions: List[BoundingBox]
    confidence_scores: List[float]
    inference_time_ms: float
    correct: Optional[bool] = None
    iou: Optional[float] = None

    class Config:
        from_attributes = True


class SingleImageTestRequest(BaseModel):
    model_id: UUID
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    confidence_threshold: float = Field(default=0.5, ge=0, le=1)
    iou_threshold: float = Field(default=0.45, ge=0, le=1)
    max_detections: int = Field(default=100, ge=1, le=1000)
    return_annotated_image: bool = True
    edge_simulator: Optional['EdgeSimulatorConfig'] = None


class EdgeSimulatorConfig(BaseModel):
    enabled: bool = False
    device: str = "jetson_nano"
    simulate_latency_ms: Optional[float] = None
    memory_limit_mb: Optional[float] = None
    power_limit_watts: Optional[float] = None


class PredictionCreate(BaseModel):
    name: str
    metric_type: str
    source_id: Optional[str] = None
    forecast_model: str = "prophet"
    horizon_hours: int = Field(default=24, ge=1, le=168)
    training_window_days: int = Field(default=30, ge=1, le=365)
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99)
    include_anomaly_detection: bool = True
    anomaly_method: str = "isolation_forest"
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    seasonal_periods: Optional[List[int]] = None


class ForecastPoint(BaseModel):
    timestamp: Union[str, datetime]
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


class AnomalyPoint(BaseModel):
    timestamp: Union[str, datetime]
    value: float
    anomaly_score: float
    is_anomaly: bool
    threshold: float
    severity: str


class PredictionResponse(BaseModel):
    id: UUID
    name: str
    metric_type: str
    source_id: Optional[str] = None
    forecast_model: str
    horizon_hours: int
    status: JobStatus
    forecast_points: List[ForecastPoint] = Field(default_factory=list)
    anomalies: Optional[List[AnomalyPoint]] = None
    confidence_level: float = 0.95
    training_metrics: Dict[str, float] = Field(default_factory=dict)
    cross_validation_metrics: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_uri: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WhatIfScenario(BaseModel):
    base_prediction_id: UUID
    modifications: Dict[str, float]
    description: Optional[str] = None


class WhatIfResponse(BaseModel):
    base_forecast: List[ForecastPoint]
    modified_forecast: List[ForecastPoint]
    delta: List[Dict[str, float]]
    impact_summary: Dict[str, float]


class MLModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    format: ModelFormat
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class MLModelCreate(MLModelBase):
    file_path: Optional[str] = None
    mlflow_model_uri: Optional[str] = None
    dataset_version: Optional[str] = None
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)


class MLModelResponse(MLModelBase):
    id: UUID
    stage: ModelStage
    file_size_bytes: Optional[int] = None
    file_hash: Optional[str] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    mlflow_run_id: Optional[str] = None
    mlflow_model_uri: Optional[str] = None
    dataset_version: Optional[str] = None
    dataset_hash: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0

    class Config:
        from_attributes = True


class ModelPromoteRequest(BaseModel):
    stage: ModelStage
    archive_previous: bool = True
