from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class Language(str, Enum):
    """Supported braille languages."""
    EN_UEB_G1 = "en-ueb-g1"
    EN_UEB_G2 = "en-ueb-g2"
    ZH_HK = "zh-hk"


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    text: str
    confidence: float


class JobSubmitResponse(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.PENDING


class JobResult(BaseModel):
    extracted_text: str
    classification: str
    confidence: float
    bounding_boxes: List[BoundingBox]
    annotated_image_url: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[JobResult] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
