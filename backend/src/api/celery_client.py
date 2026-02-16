from celery import Celery

from ..common.config import settings


def create_celery_client() -> Celery:
    """Create Celery client for sending tasks.
    
    This client only sends tasks - it doesn't import or execute them.
    This allows the API to remain lightweight without worker dependencies.
    """
    client = Celery(
        "ocr_worker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    
    client.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    
    return client


# Single instance for the API
celery_client = create_celery_client()
