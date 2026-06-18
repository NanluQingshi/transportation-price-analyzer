import asyncio
from datetime import date, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.amadeus import AmadeusAdapter
from src.db.session import AsyncSessionLocal
from src.models.price_snapshot import PriceSnapshot
from src.models.watched_route import WatchedRoute

logger = structlog.get_logger(__name__)

# 每次快照抓取未来 N 天内出发的最低价
SNAPSHOT_DAYS_AHEAD = 7


async def _fetch_and_save_route(
    adapter: AmadeusAdapter,
    origin: str,
    destination: str,
) -> int:
    """抓取一条航线未来 N 天的最低价快照，返回写入的记录数。"""
    snapshots: list[PriceSnapshot] = []
    today = date.today()

    for delta in range(1, SNAPSHOT_DAYS_AHEAD + 1):
        dep_date = today + timedelta(days=delta)
        try:
            offers = await adapter.search_flights(
                origin=origin,
                destination=destination,
                departure_date=dep_date,
            )
            for offer in offers:
                snapshots.append(
                    PriceSnapshot(
                        origin=offer.origin,
                        destination=offer.destination,
                        departure_date=offer.departure_date,
                        airline=offer.airline_code,
                        flight_number=offer.flight_number,
                        price=offer.price,
                        currency=offer.currency,
                        cabin_class=offer.cabin_class,
                        source=offer.source,
                    )
                )
        except Exception as exc:
            logger.warning(
                "snapshot_fetch_error",
                origin=origin,
                destination=destination,
                departure_date=str(dep_date),
                error=str(exc),
            )

    if snapshots:
        async with AsyncSessionLocal() as db:
            db.add_all(snapshots)
            await db.commit()

    return len(snapshots)


async def run_daily_snapshot() -> None:
    """定时任务入口：抓取所有活跃关注航线的价格快照。幂等设计——重跑只会追加数据。"""
    log = logger.bind(job="daily_snapshot")
    log.info("snapshot_job_started")

    adapter = AmadeusAdapter()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WatchedRoute).where(WatchedRoute.is_active == True)  # noqa: E712
        )
        routes = result.scalars().all()

    if not routes:
        log.warning("snapshot_no_routes", message="watched_routes 表为空，跳过")
        return

    tasks = [
        _fetch_and_save_route(adapter, route.origin, route.destination)
        for route in routes
    ]
    counts = await asyncio.gather(*tasks, return_exceptions=True)

    total = sum(c for c in counts if isinstance(c, int))
    errors = sum(1 for c in counts if isinstance(c, Exception))
    log.info("snapshot_job_finished", routes=len(routes), records_written=total, errors=errors)

    # 快照写入完成后检查价格提醒
    from src.services.alert_service import check_and_notify  # 局部导入避免循环依赖
    await check_and_notify()
