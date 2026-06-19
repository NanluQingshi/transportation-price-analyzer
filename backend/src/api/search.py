from fastapi import APIRouter, HTTPException, Query

from src.formatters.price_formatter import format_airport, format_flight_offer
from src.schemas.search import AirportSearchResponse, SearchRequest, SearchResponse
from src.services import flight_service


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_flights(req: SearchRequest) -> SearchResponse:
    try:
        offers, cached, elapsed = await flight_service.search_flights(
            origin=req.origin,
            destination=req.destination,
            departure_date=req.departure_date,
            return_date=req.return_date,
            adults=req.adults,
            cabin_class=req.cabin_class,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Flight data source error: {exc}") from exc

    return SearchResponse(
        results=[format_flight_offer(o) for o in offers],
        cached=cached,
        query_time_ms=elapsed,
    )


@router.get("/airports", response_model=AirportSearchResponse)
async def search_airports(q: str = Query(min_length=2)) -> AirportSearchResponse:
    try:
        results = await flight_service.search_airports(q)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Airport search error: {exc}") from exc

    return AirportSearchResponse(airports=[format_airport(r) for r in results])
