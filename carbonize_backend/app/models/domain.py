"""
SQLAlchemy ORM models
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, JSON, 
    ForeignKey, Index, Text, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


class ModelStage(str, enum.Enum):
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class ModelFormat(str, enum.Enum):
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    TFLITE = "tflite"
    COREML = "coreml"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    stage = Column(SQLEnum(ModelStage), default=ModelStage.NONE, nullable=False)
    format = Column(SQLEnum(ModelFormat), nullable=False)
    
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64))
    
    metrics = Column(JSONB, default=dict)
    hyperparameters = Column(JSONB, default=dict)
    
    mlflow_run_id = Column(String(64), index=True)
    mlflow_model_uri = Column(String(500))
    dataset_version = Column(String(64))
    dataset_hash = Column(String(64))
    
    description = Column(Text)
    tags = Column(ARRAY(String), default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    inferences = relationship("InferenceLog", back_populates="model")
    test_runs = relationship("TestRun", back_populates="model", foreign_keys="[TestRun.model_id]")
    
    __table_args__ = (
        Index('idx_model_name_version', 'name', 'version', unique=True),
        Index('idx_model_stage', 'stage'),
    )


class InferenceLog(Base):
    __tablename__ = "inference_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ml_models.id'), nullable=False)
    
    request_id = Column(String(64), index=True)
    user_id = Column(String(255))
    api_key_id = Column(String(64))
    input_type = Column(String(50))
    input_size_bytes = Column(Integer)
    input_dimensions = Column(JSONB)
    
    preprocessing_ms = Column(Float)
    inference_ms = Column(Float)
    postprocessing_ms = Column(Float)
    total_ms = Column(Float)
    
    detections_count = Column(Integer, default=0)
    avg_confidence = Column(Float)
    detections = Column(JSONB)
    
    gpu_memory_mb = Column(Float)
    cpu_percent = Column(Float)
    batch_size = Column(Integer, default=1)
    
    success = Column(Boolean, default=True)
    error_type = Column(String(100))
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    model = relationship("MLModel", back_populates="inferences")
    
    __table_args__ = (
        Index('idx_inference_model_time', 'model_id', 'created_at'),
        Index('idx_inference_success', 'success', 'created_at'),
    )


class TestRun(Base):
    __tablename__ = "test_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ml_models.id'), nullable=False)
    model_version = Column(String(50))
    
    test_type = Column(String(50))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id'))
    
    config = Column(JSONB, default=dict)
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    
    total_samples = Column(Integer, default=0)
    processed_samples = Column(Integer, default=0)
    failed_samples = Column(Integer, default=0)
    
    metrics = Column(JSONB, default=dict)
    per_class_metrics = Column(JSONB, default=dict)
    confusion_matrix = Column(JSONB)
    
    comparison_model_id = Column(UUID(as_uuid=True), ForeignKey('ml_models.id'))
    comparison_metrics = Column(JSONB)
    
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    celery_task_id = Column(String(64))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    
    model = relationship("MLModel", back_populates="test_runs", foreign_keys=[model_id])
    comparison_model = relationship("MLModel", foreign_keys=[comparison_model_id])
    dataset = relationship("Dataset")
    predictions = relationship("TestPrediction", back_populates="test_run")


class TestPrediction(Base):
    __tablename__ = "test_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id'), nullable=False)
    sample_id = Column(String(255), index=True)
    
    image_path = Column(String(500))
    image_url = Column(String(500))
    image_hash = Column(String(64))
    ground_truth = Column(JSONB)
    
    predictions = Column(JSONB)
    confidence_scores = Column(ARRAY(Float))
    inference_time_ms = Column(Float)
    
    comparison_predictions = Column(JSONB)
    comparison_confidence = Column(ARRAY(Float))
    
    correct = Column(Boolean)
    iou = Column(Float)
    true_positives = Column(Integer)
    false_positives = Column(Integer)
    false_negatives = Column(Integer)
    
    test_run = relationship("TestRun", back_populates="predictions")


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    
    storage_path = Column(String(500))
    format = Column(String(50))
    
    total_samples = Column(Integer)
    total_classes = Column(Integer)
    class_distribution = Column(JSONB)
    split_info = Column(JSONB)
    
    file_hash = Column(String(64), unique=True)
    
    tags = Column(ARRAY(String), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    metric_type = Column(String(100))
    source_id = Column(String(255))
    
    forecast_model = Column(String(50))
    forecast_model_uri = Column(String(500))
    
    horizon_hours = Column(Integer)
    training_window_days = Column(Integer)
    hyperparameters = Column(JSONB)
    seasonal_periods = Column(ARRAY(Integer))
    
    historical_data_path = Column(String(500))
    
    forecast_points = Column(JSONB)
    confidence_level = Column(Float, default=0.95)
    
    anomalies = Column(JSONB)
    anomaly_threshold = Column(Float)
    
    training_metrics = Column(JSONB)
    cross_validation_metrics = Column(JSONB)
    feature_importance = Column(JSONB)
    model_uri = Column(String(500))
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    expires_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_prediction_metric_source', 'metric_type', 'source_id'),
        Index('idx_prediction_status', 'status'),
    )


class DriftReport(Base):
    __tablename__ = "drift_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ml_models.id'), nullable=False)
    
    reference_window_start = Column(DateTime(timezone=True))
    reference_window_end = Column(DateTime(timezone=True))
    test_window_start = Column(DateTime(timezone=True))
    test_window_end = Column(DateTime(timezone=True))
    method = Column(String(50))
    
    overall_drift_detected = Column(Boolean)
    overall_score = Column(Float)
    features_drift = Column(JSONB)
    
    recommended_action = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
