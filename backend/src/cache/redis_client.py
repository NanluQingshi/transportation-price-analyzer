import json
from typing import Any

import redis.asyncio as aioredis

from src.config import settings

_redis: aioredis.Redis | None = None  # type: ignore[type-arg]


def get_redis() -> aioredis.Redis:  # type: ignore[type-arg]
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Any | None:
    client = get_redis()
    raw = await client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    client = get_redis()
    ttl = ttl if ttl is not None else settings.cache_ttl_seconds
    await client.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    client = get_redis()
    await client.delete(key)
