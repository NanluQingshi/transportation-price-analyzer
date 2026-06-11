from fastapi import APIRouter
from sqlalchemy import text

from src.cache.redis_client import get_redis
from src.db.session import AsyncSessionLocal

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str | dict[str, str]]:
    status: dict[str, str] = {}

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as exc:
        status["database"] = f"error: {exc}"

    try:
        redis = get_redis()
        await redis.ping()
        status["redis"] = "ok"
    except Exception as exc:
        status["redis"] = f"error: {exc}"

    overall = "ok" if all(v == "ok" for v in status.values()) else "degraded"
    return {"status": overall, "services": status}
