import json
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from redis import Redis
from celery.result import AsyncResult

from ...common.schemas import JobSubmitResponse, JobStatusResponse, JobStatus, Language
from ..dependencies import get_redis_client
from ..celery_client import celery_client
from ...common import storage

router = APIRouter(prefix="/jobs", tags=["inference"])


@router.post("", response_model=JobSubmitResponse)
async def submit_job(
    file: Annotated[UploadFile, File(description="Image file to process")],
    language: Annotated[Optional[Language], Form(description="Optional: Braille code or language. If not provided, language will be auto-detected.")] = None,
    redis_client: Redis = Depends(get_redis_client),
):
    """Submit an image for OCR processing.
    
    Returns immediately with a job_id. Poll GET /jobs/{job_id} for results.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    filepath = storage.save_upload(file.file, file.filename)
    language_value = language.value if language else None
    
    # Submit task to Celery
    task = celery_client.send_task('process_image', args=[filepath, language_value])
    job_id = task.id
    
    # Store job metadata in Redis
    job_meta = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "filename": file.filename,
    }
    redis_client.setex(
        f"job:{job_id}:meta",
        3600,  # 1 hour TTL
        json.dumps(job_meta),
    )
    
    return JobSubmitResponse(job_id=job_id, status=JobStatus.PENDING)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    redis_client: Redis = Depends(get_redis_client),
):
    """Get the status and result of a job.
    
    Poll this endpoint until status is 'success' or 'failed'.
    """
    
    # Get task result from Celery
    task_result = AsyncResult(job_id)
    
    # Get job metadata
    meta_key = f"job:{job_id}:meta"
    meta_data = redis_client.get(meta_key)
    
    if not meta_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_meta = json.loads(meta_data)
    
    # Map Celery state to our JobStatus
    status_map = {
        "PENDING": JobStatus.PENDING,
        "STARTED": JobStatus.PROCESSING,
        "SUCCESS": JobStatus.SUCCESS,
        "FAILURE": JobStatus.FAILED,
        "RETRY": JobStatus.PROCESSING,
    }
    
    status = status_map.get(task_result.state, JobStatus.PENDING)
    
    response = JobStatusResponse(
        job_id=job_id,
        status=status,
        created_at=job_meta.get("created_at"),
    )
    
    if status == JobStatus.SUCCESS:
        response.result = task_result.result
        response.completed_at = datetime.utcnow().isoformat()
    elif status == JobStatus.FAILED:
        response.error = str(task_result.info)
        response.completed_at = datetime.utcnow().isoformat()
    
    return response
