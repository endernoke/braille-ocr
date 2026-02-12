import redis
from functools import lru_cache

from ..common.config import settings


@lru_cache()
def get_redis_client() -> redis.Redis:
    """Get Redis client instance (cached)."""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )
