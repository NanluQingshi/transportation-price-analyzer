import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.watched_route import WatchedRoute
from src.schemas.routes import RouteResponse

logger = structlog.get_logger(__name__)


async def list_routes(db: AsyncSession) -> list[RouteResponse]:
    result = await db.execute(select(WatchedRoute).order_by(WatchedRoute.id))
    rows = result.scalars().all()
    return [RouteResponse(
        id=r.id,
        origin=r.origin,
        destination=r.destination,
        is_active=r.is_active,
        created_at=r.created_at,
    ) for r in rows]


async def create_route(db: AsyncSession, origin: str, destination: str) -> RouteResponse:
    existing = await db.execute(
        select(WatchedRoute).where(
            WatchedRoute.origin == origin,
            WatchedRoute.destination == destination,
        )
    )
    row = existing.scalar_one_or_none()
    if row:
        # 已存在但被停用则重新激活
        if not row.is_active:
            row.is_active = True
            await db.commit()
            await db.refresh(row)
            logger.info("route_reactivated", origin=origin, destination=destination)
        return RouteResponse(
            id=row.id, origin=row.origin, destination=row.destination,
            is_active=row.is_active, created_at=row.created_at,
        )

    new_route = WatchedRoute(origin=origin, destination=destination)
    db.add(new_route)
    await db.commit()
    await db.refresh(new_route)
    logger.info("route_created", origin=origin, destination=destination)
    return RouteResponse(
        id=new_route.id, origin=new_route.origin, destination=new_route.destination,
        is_active=new_route.is_active, created_at=new_route.created_at,
    )


async def delete_route(db: AsyncSession, route_id: int) -> bool:
    """软删除：设为 inactive。返回 True 表示找到并删除，False 表示不存在。"""
    result = await db.execute(select(WatchedRoute).where(WatchedRoute.id == route_id))
    row = result.scalar_one_or_none()
    if not row:
        return False
    row.is_active = False
    await db.commit()
    logger.info("route_deactivated", id=route_id, origin=row.origin, destination=row.destination)
    return True
