from datetime import date, timedelta

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.price_snapshot import PriceSnapshot
from src.models.watched_route import WatchedRoute
from src.schemas.dashboard import DashboardResponse, RouteSummary

logger = structlog.get_logger(__name__)

# 默认热门航线（数据库无关注航线时的兜底）
DEFAULT_ROUTES = [
    ("PEK", "SHA", "北京", "上海"),
    ("PEK", "CAN", "北京", "广州"),
    ("SHA", "CAN", "上海", "广州"),
    ("PEK", "CTU", "北京", "成都"),
    ("SHA", "CTU", "上海", "成都"),
]


async def get_dashboard(db: AsyncSession) -> DashboardResponse:
    today = date.today()
    yesterday = today - timedelta(days=1)

    # 取关注航线，fallback 到默认列表
    routes_result = await db.execute(
        select(WatchedRoute).where(WatchedRoute.is_active == True)  # noqa: E712
    )
    watched = routes_result.scalars().all()
    route_pairs = (
        [(r.origin, r.destination, "", "") for r in watched] if watched else DEFAULT_ROUTES
    )

    summaries: list[RouteSummary] = []
    for origin, destination, origin_city, dest_city in route_pairs:
        today_price = await _min_price_on_date(db, origin, destination, today)
        yesterday_price = await _min_price_on_date(db, origin, destination, yesterday)

        if today_price is None:
            continue

        change = (today_price - yesterday_price) if yesterday_price else 0.0
        change_pct = (change / yesterday_price * 100) if yesterday_price else 0.0
        trend = "stable" if abs(change_pct) < 1 else ("up" if change > 0 else "down")

        summaries.append(
            RouteSummary(
                origin=origin,
                destination=destination,
                origin_city=origin_city,
                destination_city=dest_city,
                min_price=today_price,
                currency="CNY",
                price_change=round(change, 2),
                price_change_pct=round(change_pct, 1),
                trend=trend,
            )
        )

    return DashboardResponse(date=today, routes=summaries)


async def _min_price_on_date(
    db: AsyncSession, origin: str, destination: str, target: date
) -> float | None:
    result = await db.execute(
        select(func.min(PriceSnapshot.price)).where(
            PriceSnapshot.origin == origin,
            PriceSnapshot.destination == destination,
            PriceSnapshot.captured_at >= text(f"'{target}'::date"),
            PriceSnapshot.captured_at < text(f"'{target + timedelta(days=1)}'::date"),
        )
    )
    val = result.scalar()
    return float(val) if val is not None else None
