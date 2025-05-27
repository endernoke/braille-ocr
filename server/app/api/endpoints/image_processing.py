import io
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Form
from PIL import Image
import logging
from copy import deepcopy

from app.core import tasks
from app.core.processing import process_braille_image, image_processing_lock
from app.api.schemas import TaskCreationResponse, TaskStatusResponse, TaskResultResponse

router = APIRouter()

async def run_image_processing_logic(task_id: str, image_data: bytes, original_filename: str, lang: str):
    """Background task for processing the image."""
    try:
        # Process image with lock (non-thread-safe operation)
        async with image_processing_lock:
            # Update task status to processing
            tasks.update_task_status(task_id, "processing")
            # Convert bytes back to PIL Image
            image = Image.open(io.BytesIO(image_data))
            result = await process_braille_image(image, original_filename, lang=lang)
        
        # Store successful result
        tasks.store_task_result(task_id, result.model_dump())
        
    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        tasks.store_task_error(task_id, f"Image processing failed: {str(e)}")

@router.post("/process-image", response_model=TaskCreationResponse, status_code=202)
async def submit_image_for_processing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    lang: str = Form(""),
):
    print("Received language: ", lang)
    try:
        # Try to open and validate the image
        image_data = await file.read()
        try:
            Image.open(io.BytesIO(image_data))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Create a new task
        task_id = tasks.create_task(file.filename)
        
        # Schedule the background processing
        background_tasks.add_task(
            run_image_processing_logic,
            task_id,
            image_data,
            original_filename=file.filename,
            lang=lang,
        )
        
        return TaskCreationResponse(
            task_id=task_id,
            status="pending",
            message="Image accepted for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task_info = tasks.get_task_info(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_info["status"],
    )

@router.get("/tasks/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    task_info = deepcopy(tasks.get_task_info(task_id))
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = TaskResultResponse(
        task_id=task_id,
        status=task_info["status"],
    )
    
    if task_info["status"] == "completed":
        response.result = task_info["result"]
    elif task_info["status"] == "failed":
        response.error = task_info["error_message"]
    else:
        response.message = "Processing not yet complete"
        return response, 202

    # Clean up the task info after retrieval (to avoid memory leaks)
    del tasks.tasks_db[task_id]

    return response
