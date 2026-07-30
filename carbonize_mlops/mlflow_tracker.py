"""
Production MLflow Tracker for YOLO Models
Fixes Bottleneck B5: Model versioning drift
"""

import mlflow
import mlflow.yolo
from pathlib import Path
from datetime import datetime
import json
import hashlib
from typing import Dict, Any


class CarbonizeModelRegistry:
    """Track, version, and promote YOLO models through stages."""
    
    def __init__(self, tracking_uri: str = "http://mlflow-server:5000",
                 experiment_name: str = "carbonize_carbon_capture"):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name
    
    def log_model(self, model_path: str, metrics: Dict[str, float],
                  params: Dict[str, Any], dataset_version: str,
                  tags: Dict[str, str] = None) -> str:
        """Log a YOLO model with full lineage."""
        with mlflow.start_run(run_name=f"yolo_{datetime.utcnow().isoformat()}"):
            # Params
            mlflow.log_params(params)
            
            # Metrics
            mlflow.log_metrics(metrics)
            
            # Tags
            if tags:
                mlflow.set_tags(tags)
            mlflow.set_tag("dataset_version", dataset_version)
            
            # Model artifact
            model_uri = mlflow.yolo.log_model(
                model_path,
                artifact_path="model",
                registered_model_name="carbonize_yolo"
            ).model_uri
            
            # Dataset hash for reproducibility
            dataset_hash = self._hash_dataset(dataset_version)
            mlflow.set_tag("dataset_hash", dataset_hash)
            
            return model_uri
    
    def promote(self, version: int, stage: str = "Production") -> None:
        """Promote a model version to a stage (None/Staging/Production/Archived)."""
        client = mlflow.MlflowClient()
        client.transition_model_version_stage(
            name="carbonize_yolo",
            version=version,
            stage=stage
        )
    
    def load_production(self) -> str:
        """Load current production model URI."""
        client = mlflow.MlflowClient()
        versions = client.get_latest_versions("carbonize_yolo", stages=["Production"])
        if not versions:
            raise RuntimeError("No production model registered")
        return versions[0].source
    
    @staticmethod
    def _hash_dataset(dataset_path: str) -> str:
        """SHA-256 hash of dataset manifest for reproducibility."""
        path = Path(dataset_path)
        if not path.exists():
            return "unknown"
        if path.is_file():
            return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        # Hash directory contents
        sha = hashlib.sha256()
        for f in sorted(path.rglob("*")):
            if f.is_file():
                sha.update(f.read_bytes())
        return sha.hexdigest()[:16]
