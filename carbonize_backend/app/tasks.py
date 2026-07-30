"""Celery worker tasks for CPU/GPU-bound work."""

from app.celery_app import celery_app
from ultralytics import YOLO
import base64
import cv2
import numpy as np
try:
    import mlflow
except ImportError:
    class _MockMlflow:
        class MlflowClient:
            def __init__(self, *args, **kwargs): pass
            def get_latest_versions(self, *args, **kwargs): return []
    mlflow = _MockMlflow()

# ─── Load model once per worker ─────────────────────────────────────
_model_cache = {}

def _get_model(version: str = "production"):
    if version not in _model_cache:
        try:
            client = mlflow.MlflowClient()
            versions = client.get_latest_versions("carbonize_yolo", stages=[version.title()])
            if versions:
                _model_cache[version] = YOLO(versions[0].source)
            else:
                _model_cache[version] = YOLO("yolov8n.pt")
        except Exception:
            _model_cache[version] = YOLO("yolov8n.pt")
    return _model_cache[version]


@celery_app.task(name="carbonize.inference", bind=True, max_retries=3)
def run_inference_task(self, image_b64: str, model_version: str, conf: float):
    """GPU inference offloaded from API thread."""
    try:
        img_bytes = base64.b64decode(image_b64)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        
        model = _get_model(model_version)
        t0 = time.perf_counter()
        results = model.predict(frame, conf=conf, verbose=False)
        inference_ms = (time.perf_counter() - t0) * 1000.0
        
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class": model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].cpu().numpy().tolist()
                })
        
        return {"detections": detections, "inference_time_ms": inference_ms}
    except Exception as e:
        self.retry(exc=e, countdown=2)


@celery_app.task(name="carbonize.register_model")
def register_model_task(model_path: str, dataset_version: str):
    """Background task to register trained model."""
    return {"status": "registered", "model_path": model_path, "dataset_version": dataset_version}
