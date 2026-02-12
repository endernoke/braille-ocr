# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- (Optional) NVIDIA Docker runtime for GPU support

## Setup

1. **Initial setup:**
   ```bash
   bash scripts/setup_dev.sh
   ```

2. **Edit environment variables (if needed):**
   ```bash
   nano .env
   ```

## Running the Application

### Development Mode (with GPU)

```bash
docker compose --profile app up --build
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### CPU-Only Mode

```bash
docker compose -f docker-compose.yml -f docker-compose.cpu.yml --profile app up --build
```

### Production Mode

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile app up -d

# Scale workers
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale worker=3
```

## Training Models

```bash
# Run OCR training
docker compose --profile training run training python scripts/train_ocr.py --config configs/ocr_baseline.yaml

# Run classifier training
docker compose --profile training run training python scripts/train_classifier.py --config configs/classifier_baseline.yaml
```

## Development Workflow

### Backend Development

```bash
# Install dependencies locally
cd backend
pip install -e ".[dev]"

# Run tests
pytest

# Run API server locally (without Docker)
uvicorn src.api.main:app --reload
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

### C Library Development

```bash
cd c_library
make clean
make
sudo make install
```

## Useful Commands

### View logs
```bash
# All services
docker compose --profile app logs -f

# Specific service
docker compose logs -f worker
```

### Stop services
```bash
docker compose --profile app down
```

### Rebuild specific service
```bash
docker compose --profile app build worker
docker compose --profile app up -d worker
```

### Access container shell
```bash
docker exec -it ocr-worker bash
```

### Monitor Celery workers
```bash
docker exec -it ocr-worker celery -A src.worker.celery_app inspect active
docker exec -it ocr-worker celery -A src.worker.celery_app inspect stats
```

## API Usage

### Submit a job
```bash
curl -X POST http://localhost:8000/api/jobs \
  -F "file=@/path/to/image.jpg"
```

Response:
```json
{
  "job_id": "abc123...",
  "status": "pending"
}
```

### Check job status
```bash
curl http://localhost:8000/api/jobs/abc123...
```

## Project Structure Summary

```
new-project/
├── backend/               # Python backend (API + Worker + ML)
│   ├── src/
│   │   ├── api/          # FastAPI routes and schemas
│   │   ├── worker/       # Celery tasks
│   │   ├── ml/           # ML models and inference
│   │   └── common/       # Shared utilities
│   ├── tests/            # Unit tests
│   └── requirements/     # Python dependencies
│
├── frontend/             # React SPA
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── pages/       # Page components
│   └── nginx.conf       # Nginx configuration
│
├── training/             # Training scripts and configs
│   ├── scripts/         # Training scripts
│   ├── configs/         # Experiment configs
│   └── notebooks/       # Jupyter notebooks
│
├── c_library/            # Custom C library
│   ├── src/             # C source code
│   ├── include/         # Headers
│   └── Makefile         # Build configuration
│
└── docker-compose.yml    # Service orchestration
```

## Next Steps

1. **Replace ML stubs with real models:**
   - Implement actual OCR model architecture in `backend/src/ml/ocr/model.py`
   - Implement classifier in `backend/src/ml/classifier/model.py`
   - Update inference engines with real preprocessing and postprocessing

2. **Implement C library:**
   - Add actual postprocessing logic in `c_library/src/postprocess.c`
   - Update Python bindings in `backend/src/ml/postprocessing/c_bindings.py`

3. **Add training datasets:**
   - Place training data in `data/` directory
   - Implement dataset loaders in training scripts

4. **Enhance frontend:**
   - Add more visualizations
   - Implement image cropping/editing
   - Add user authentication

5. **Production hardening:**
   - Add proper logging and monitoring
   - Implement rate limiting
   - Add database for persistent storage
   - Set up CI/CD pipeline
   - Add security headers and HTTPS
