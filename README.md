# ML OCR Full Stack Application

A production-grade OCR application with machine learning inference, text classification, and post-processing.

## Architecture

- **Frontend**: React SPA (served via nginx)
- **API**: FastAPI (Python, CPU-only)
- **Worker**: Celery with PyTorch models (GPU-enabled)
- **Broker**: Redis (message queue + result backend)

## Features

- Upload images for OCR processing
- PyTorch-based text detection and recognition
- Text classification using a secondary model
- Custom C library post-processing
- GPU acceleration with CPU fallback
- Asynchronous job processing with status polling

## Project Structure

```
new-project/
├── frontend/          # React SPA
├── backend/           # Python API and worker code
├── training/          # Model training scripts
├── c_library/         # Custom C library with Python bindings
├── models/            # Trained model weights (gitignored)
├── data/              # Training data (gitignored)
└── docker-compose.yml # Service orchestration
```

## Quick Start

### Development

```bash
# Copy environment variables
cp .env.example .env

# Start all services
docker compose --profile app up --build

# Frontend will be available at http://localhost:3000
# API docs at http://localhost:8000/docs
```

### Training

```bash
# Run training
docker compose --profile training run training python scripts/train_ocr.py
```

### CPU-only mode

```bash
# Use CPU-only compose file
docker compose -f docker-compose.yml -f docker-compose.cpu.yml --profile app up
```

## Development Setup

### Backend

```bash
cd backend
pip install -e ".[dev]"
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/jobs` - Submit image for processing
- `GET /api/jobs/{job_id}` - Get job status and results
- `GET /health` - Health check

## License

MIT
