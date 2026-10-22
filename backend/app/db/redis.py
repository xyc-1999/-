"""Redis 客户端单例（会话记忆 / 缓存）。"""
from functools import lru_cache

import redis

from app.core.config import settings


@lru_cache
def get_redis_pool() -> redis.Redis:
    """返回全局 Redis 连接（连接池复用）。"""
    return redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,  # 默认返回 str 而非 bytes
        socket_timeout=5,
        socket_connect_timeout=5,
    )


redis_client = get_redis_pool()