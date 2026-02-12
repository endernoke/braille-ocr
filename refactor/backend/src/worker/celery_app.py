from celery import Celery

from ..common.config import settings

celery_app = Celery(
    "ocr_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=270,  # Soft limit at 4.5 minutes
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,  # Take one task at a time (for GPU)
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory cleanup)
)

# Import tasks to register them
from . import tasks
