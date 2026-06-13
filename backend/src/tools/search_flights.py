from datetime import date
from pathlib import Path

from src.adapters.amadeus import AmadeusAdapter
from src.adapters.base import FlightOffer

TOOL_SCHEMA = {
    "name": "search_flights",
    "description": Path(__file__).parent.parent.parent / "prompts/tools/search_flights.md",
    "input_schema": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": "出发机场 IATA 代码，3位大写字母，如 PEK",
            },
            "destination": {
                "type": "string",
                "description": "到达机场 IATA 代码，3位大写字母，如 SHA",
            },
            "departure_date": {
                "type": "string",
                "description": "出发日期，格式 YYYY-MM-DD",
            },
            "adults": {
                "type": "integer",
                "description": "乘客人数，默认 1",
                "default": 1,
            },
        },
        "required": ["origin", "destination", "departure_date"],
    },
}


def _load_description() -> str:
    path = Path(__file__).parent.parent.parent / "prompts/tools/search_flights.md"
    return path.read_text(encoding="utf-8").strip()


def get_schema() -> dict:  # type: ignore[type-arg]
    schema = dict(TOOL_SCHEMA)
    schema["description"] = _load_description()
    return schema


async def execute(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
) -> dict:  # type: ignore[type-arg]
    adapter = AmadeusAdapter()
    dep = date.fromisoformat(departure_date)
    offers: list[FlightOffer] = await adapter.search_flights(
        origin=origin,
        destination=destination,
        departure_date=dep,
        adults=adults,
    )
    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "offers": [
            {
                "flight_number": o.flight_number,
                "airline": o.airline,
                "departure_time": o.departure_time,
                "arrival_time": o.arrival_time,
                "duration_minutes": o.duration_minutes,
                "price": o.price,
                "currency": o.currency,
                "cabin_class": o.cabin_class,
            }
            for o in sorted(offers, key=lambda x: x.price)[:10]
        ],
        "total_found": len(offers),
    }
