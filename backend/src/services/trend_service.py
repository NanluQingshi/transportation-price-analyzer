from datetime import date, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.price_snapshot import PriceSnapshot
from src.schemas.trends import PriceDataPoint, PriceStats, TrendsResponse

logger = structlog.get_logger(__name__)


def _price_level(current: float, avg: float, historical_min: float) -> str:
    """把当前价格相对历史均价的偏离程度分成五档。"""
    if avg == 0:
        return "average"
    ratio = (current - avg) / avg
    if ratio < -0.15:
        return "low"
    if ratio < -0.05:
        return "below_average"
    if ratio <= 0.05:
        return "average"
    if ratio <= 0.15:
        return "above_average"
    return "high"


async def get_trends(
    db: AsyncSession,
    origin: str,
    destination: str,
    days: int,
) -> TrendsResponse:
    since = date.today() - timedelta(days=days)

    rows = await db.execute(
        select(
            func.date(PriceSnapshot.captured_at).label("snap_date"),
            func.min(PriceSnapshot.price).label("min_price"),
            func.avg(PriceSnapshot.price).label("avg_price"),
            func.max(PriceSnapshot.price).label("max_price"),
        )
        .where(
            PriceSnapshot.origin == origin,
            PriceSnapshot.destination == destination,
            func.date(PriceSnapshot.captured_at) >= since,
        )
        .group_by(func.date(PriceSnapshot.captured_at))
        .order_by(func.date(PriceSnapshot.captured_at))
    )
    records = rows.all()

    data_points = [
        PriceDataPoint(
            date=row.snap_date,
            min_price=float(row.min_price),
            avg_price=round(float(row.avg_price), 2),
            max_price=float(row.max_price),
            currency="CNY",
        )
        for row in records
    ]

    if data_points:
        all_mins = [p.min_price for p in data_points]
        all_avgs = [p.avg_price for p in data_points]
        hist_min = min(all_mins)
        hist_avg = round(sum(all_avgs) / len(all_avgs), 2)
        current = data_points[-1].min_price
        level = _price_level(current, hist_avg, hist_min)
    else:
        hist_min = 0.0
        hist_avg = 0.0
        current = None
        level = "average"

    stats = PriceStats(
        historical_min=hist_min,
        historical_avg=hist_avg,
        current_price=current,
        price_level=level,
    )

    logger.info(
        "trends_query",
        origin=origin,
        destination=destination,
        days=days,
        data_points=len(data_points),
    )
    return TrendsResponse(
        origin=origin,
        destination=destination,
        days=days,
        data_points=data_points,
        stats=stats,
    )
