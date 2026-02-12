from .health import router as health_router
from .inference import router as inference_router

__all__ = ["health_router", "inference_router"]
