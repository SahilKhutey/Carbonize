"""
Celery application setup for async tasks
"""
from celery import Celery
import logging

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    'carbonize',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
)
