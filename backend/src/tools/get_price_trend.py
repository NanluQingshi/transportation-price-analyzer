from pathlib import Path

from src.db.session import AsyncSessionLocal
from src.services.trend_service import get_trends


def _load_description() -> str:
    path = Path(__file__).parent.parent.parent / "prompts/tools/get_price_trend.md"
    return path.read_text(encoding="utf-8").strip()


def get_schema() -> dict:  # type: ignore[type-arg]
    return {
        "name": "get_price_trend",
        "description": _load_description(),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "出发机场 IATA 代码",
                },
                "destination": {
                    "type": "string",
                    "description": "到达机场 IATA 代码",
                },
                "days": {
                    "type": "integer",
                    "description": "查询最近多少天的历史数据，可选 30、90、180",
                    "enum": [30, 90, 180],
                    "default": 30,
                },
            },
            "required": ["origin", "destination"],
        },
    }


async def execute(
    origin: str,
    destination: str,
    days: int = 30,
) -> dict:  # type: ignore[type-arg]
    async with AsyncSessionLocal() as db:
        result = await get_trends(db, origin, destination, days)

    return {
        "origin": origin,
        "destination": destination,
        "days": days,
        "stats": {
            "historical_min": result.stats.historical_min,
            "historical_avg": result.stats.historical_avg,
            "current_price": result.stats.current_price,
            "price_level": result.stats.price_level,
        },
        "recent_prices": [
            {
                "date": str(p.date),
                "min_price": p.min_price,
                "avg_price": p.avg_price,
            }
            for p in result.data_points[-7:]  # 只把最近 7 天传给 Claude，避免上下文过长
        ],
        "data_points_total": len(result.data_points),
    }
