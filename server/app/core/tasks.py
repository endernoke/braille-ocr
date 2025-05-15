import uuid
from typing import Optional, Any, Dict

# In-memory task storage
tasks_db: Dict[str, dict] = {}

def create_task(filename: str) -> str:
    """Create a new task and return its ID."""
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "status": "pending",
        "filename": filename,
        "result": None,
        "error_message": None
    }
    return task_id

def update_task_status(task_id: str, status: str) -> None:
    """Update the status of a task."""
    if task_id in tasks_db:
        tasks_db[task_id]["status"] = status

def store_task_result(task_id: str, result: Any) -> None:
    """Store the result of a completed task."""
    if task_id in tasks_db:
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = result

def store_task_error(task_id: str, error_message: str) -> None:
    """Store error information for a failed task."""
    if task_id in tasks_db:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error_message"] = error_message

def get_task_info(task_id: str) -> Optional[dict]:
    """Retrieve information about a task."""
    return tasks_db.get(task_id)
