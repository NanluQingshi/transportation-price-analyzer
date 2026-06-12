from src.adapters.base import AirportInfo, FlightOffer
from src.schemas.search import AirportResponse, FlightOfferResponse


def format_flight_offer(offer: FlightOffer) -> FlightOfferResponse:
    return FlightOfferResponse(
        flight_number=offer.flight_number,
        airline=offer.airline,
        airline_code=offer.airline_code,
        origin=offer.origin,
        destination=offer.destination,
        departure_time=offer.departure_time,
        arrival_time=offer.arrival_time,
        duration_minutes=offer.duration_minutes,
        price=offer.price,
        currency=offer.currency,
        cabin_class=offer.cabin_class,
        source=offer.source,
    )


def format_airport(info: AirportInfo) -> AirportResponse:
    return AirportResponse(
        iata=info.iata_code,
        name=info.name,
        city=info.city,
        country=info.country,
    )
