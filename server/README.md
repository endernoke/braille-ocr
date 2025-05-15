# Image Processing Server

A FastAPI-based server that handles image processing tasks asynchronously. This server provides a REST API for submitting images for processing and checking the status of processing tasks.

## Features

- Static file serving from `/public` directory
- Asynchronous image processing with task status tracking
- Non-blocking API design
- Mock image processing implementation (ready for real implementation)

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

The server will start at `http://localhost:8000`

## API Documentation

### Submit an Image for Processing

**POST /api/process-image**

Submit an image for processing. The image processing is performed asynchronously.

- Request: `multipart/form-data`
  - `file`: Image file

- Response: `202 Accepted`
  ```json
  {
    "task_id": "uuid",
    "status": "pending",
    "message": "Image accepted for processing"
  }
  ```

### Check Task Status

**GET /api/tasks/{task_id}/status**

Get the current status of a processing task.

- Response: `200 OK`
  ```json
  {
    "task_id": "uuid",
    "status": "pending|processing|completed|failed",
  }
  ```

### Get Task Result

**GET /api/tasks/{task_id}/result**

Get the result of a processing task.

- Response: `200 OK` (for completed tasks)
  ```json
  {
    "task_id": "uuid",
    "status": "completed",
    "filename": "example.jpg",
    "result": {
      "original_filename": "example.jpg",
      "annotated_image": "data:image/png;base64,...", // may be null
      "recognized_braille": "braille text",
      "recognized_text": "recognized text",
    }
  }
  ```

- Response: `202 Accepted` (for pending/processing tasks)
  ```json
  {
    "task_id": "uuid",
    "status": "processing",
    "message": "Processing not yet complete"
  }
  ```

## Implementation Notes

- The server uses FastAPI's `BackgroundTasks` for asynchronous processing
- A global `asyncio.Lock` ensures that image processing is serialized (non-thread-safe operations)
- Task statuses and results are stored in memory (consider using a proper database for production)
- Static files are served from the `/public` directory
- CORS is enabled for all origins (customize for production)
