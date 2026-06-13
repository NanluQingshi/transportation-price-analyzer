from datetime import date, timedelta
from pathlib import Path

from src.adapters.amadeus import AmadeusAdapter


def _load_description() -> str:
    path = Path(__file__).parent.parent.parent / "prompts/tools/analyze_price.md"
    return path.read_text(encoding="utf-8").strip()


def get_schema() -> dict:  # type: ignore[type-arg]
    return {
        "name": "analyze_price",
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
                "target_date": {
                    "type": "string",
                    "description": "目标出行日期（中心日期），格式 YYYY-MM-DD",
                },
                "window_days": {
                    "type": "integer",
                    "description": "以 target_date 为中心，前后各查询多少天，默认 3",
                    "default": 3,
                },
            },
            "required": ["origin", "destination", "target_date"],
        },
    }


async def execute(
    origin: str,
    destination: str,
    target_date: str,
    window_days: int = 3,
) -> dict:  # type: ignore[type-arg]
    adapter = AmadeusAdapter()
    center = date.fromisoformat(target_date)
    results = []

    for delta in range(-window_days, window_days + 1):
        dep = center + timedelta(days=delta)
        if dep < date.today():
            continue
        try:
            offers = await adapter.search_flights(
                origin=origin,
                destination=destination,
                departure_date=dep,
            )
            if offers:
                min_price = min(o.price for o in offers)
                results.append({"date": str(dep), "min_price": min_price, "currency": offers[0].currency})
        except Exception:
            continue

    if not results:
        return {"origin": origin, "destination": destination, "target_date": target_date, "prices": [], "recommendation": "无法获取价格数据"}

    best = min(results, key=lambda x: x["min_price"])
    return {
        "origin": origin,
        "destination": destination,
        "target_date": target_date,
        "prices": results,
        "best_date": best["date"],
        "best_price": best["min_price"],
        "currency": best["currency"],
    }
