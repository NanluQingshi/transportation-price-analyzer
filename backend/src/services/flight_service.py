import hashlib
import json
import time
from datetime import date

import structlog

from src.adapters.amadeus import AmadeusAdapter
from src.adapters.base import AirportInfo, FlightOffer
from src.cache.redis_client import cache_get, cache_set

logger = structlog.get_logger(__name__)

_amadeus = AmadeusAdapter()


def _cache_key(
    origin: str,
    destination: str,
    departure_date: date,
    return_date: date | None,
    adults: int,
    cabin_class: str,
) -> str:
    raw = json.dumps(
        {
            "o": origin,
            "d": destination,
            "dep": departure_date.isoformat(),
            "ret": return_date.isoformat() if return_date else None,
            "pax": adults,
            "cab": cabin_class,
        },
        sort_keys=True,
    )
    return f"search:{hashlib.md5(raw.encode()).hexdigest()}"


async def search_flights(
    origin: str,
    destination: str,
    departure_date: date,
    return_date: date | None = None,
    adults: int = 1,
    cabin_class: str = "ECONOMY",
) -> tuple[list[FlightOffer], bool, int]:
    """返回 (offers, cached, query_time_ms)。"""
    key = _cache_key(origin, destination, departure_date, return_date, adults, cabin_class)

    cached = await cache_get(key)
    if cached is not None:
        offers = [FlightOffer(**item) for item in cached]
        return offers, True, 0

    t0 = time.monotonic()
    offers = await _amadeus.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
        cabin_class=cabin_class,
    )
    elapsed = int((time.monotonic() - t0) * 1000)

    serializable = [
        {**o.__dict__, "departure_date": o.departure_date.isoformat()} for o in offers
    ]
    await cache_set(key, serializable)

    logger.info("flight_search_complete", origin=origin, destination=destination, results=len(offers), ms=elapsed)
    return offers, False, elapsed


async def search_airports(query: str) -> list[AirportInfo]:
    return await _amadeus.search_airports(query)
