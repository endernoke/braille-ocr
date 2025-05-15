from pydantic import BaseModel
from typing import Optional, Any

class TaskCreationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str

class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ImageProcessingResult(BaseModel):
    original_filename: str
    annotated_image: Optional[bytes] = None
    recognized_braille: Optional[str] = None
    recognized_text: Optional[str] = None