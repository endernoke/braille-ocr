import os
import uuid
from pathlib import Path
from typing import BinaryIO

from PIL import Image

from ..common.config import settings


def ensure_dirs():
    """Ensure upload and result directories exist."""
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.result_dir).mkdir(parents=True, exist_ok=True)


def save_upload(file: BinaryIO, filename: str) -> str:
    """Save uploaded file and return the path.
    
    Args:
        file: File-like object with image data
        filename: Original filename
        
    Returns:
        Path where the file was saved
    """
    ensure_dirs()
    
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    filepath = Path(settings.upload_dir) / unique_name
    
    with open(filepath, "wb") as f:
        f.write(file.read())
    
    return str(filepath)


def save_result_image(image: Image.Image, job_id: str) -> str:
    """Save result image with bounding boxes.
    
    Args:
        image: PIL Image with annotations
        job_id: Job identifier
        
    Returns:
        Path where the result was saved
    """
    ensure_dirs()
    
    filepath = Path(settings.result_dir) / f"{job_id}.jpg"
    image.save(filepath, "JPEG", quality=95)
    
    return str(filepath)


def get_result_url(filepath: str) -> str:
    """Convert absolute filepath to URL path.
    
    Args:
        filepath: Absolute path to result file
        
    Returns:
        URL path relative to API
    """
    filename = Path(filepath).name
    return f"/results/{filename}"
