from fastapi import APIRouter, Depends
from redis import Redis

from ..dependencies import get_redis_client

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api"}


@router.get("/health/redis")
async def redis_health(redis_client: Redis = Depends(get_redis_client)):
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "service": "redis", "error": str(e)}
