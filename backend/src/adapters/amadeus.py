import re
from datetime import date

import structlog
from amadeus import Client, ResponseError
from tenacity import retry, stop_after_attempt, wait_exponential

from src.adapters.base import AirportInfo, FlightDataSource, FlightOffer
from src.config import settings

logger = structlog.get_logger(__name__)


def _parse_duration(iso_duration: str) -> int:
    """ISO 8601 duration (PT2H15M) → 分钟数。"""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


class AmadeusAdapter(FlightDataSource):
    def __init__(self) -> None:
        self._client = Client(
            client_id=settings.amadeus_client_id,
            client_secret=settings.amadeus_client_secret,
            hostname=settings.amadeus_hostname,
            log_level="silent",
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date | None = None,
        adults: int = 1,
        cabin_class: str = "ECONOMY",
    ) -> list[FlightOffer]:
        log = logger.bind(
            adapter="amadeus",
            origin=origin,
            destination=destination,
            departure_date=str(departure_date),
        )
        try:
            params: dict[str, str | int] = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date.isoformat(),
                "adults": adults,
                "travelClass": cabin_class,
                "max": 20,
            }
            if return_date:
                params["returnDate"] = return_date.isoformat()

            response = self._client.shopping.flight_offers_search.get(**params)
            offers = self._parse_flight_offers(response.data, cabin_class)
            log.info("amadeus_search_success", result_count=len(offers))
            return offers
        except ResponseError as exc:
            log.error("amadeus_search_failed", error=str(exc), status=exc.response.status_code)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    async def search_airports(self, query: str) -> list[AirportInfo]:
        log = logger.bind(adapter="amadeus", query=query)
        try:
            response = self._client.reference_data.locations.get(
                keyword=query,
                subType="AIRPORT",
            )
            airports = [
                AirportInfo(
                    iata_code=loc["iataCode"],
                    name=loc["name"],
                    city=loc["address"]["cityName"],
                    country=loc["address"]["countryName"],
                )
                for loc in response.data
            ]
            log.info("amadeus_airport_search_success", result_count=len(airports))
            return airports
        except ResponseError as exc:
            log.error("amadeus_airport_search_failed", error=str(exc))
            raise

    def _parse_flight_offers(self, data: list[dict], cabin_class: str) -> list[FlightOffer]:  # type: ignore[type-arg]
        offers: list[FlightOffer] = []
        for item in data:
            try:
                price = float(item["price"]["grandTotal"])
                currency = item["price"]["currency"]
                for itinerary in item["itineraries"]:
                    for segment in itinerary["segments"]:
                        dep = segment["departure"]
                        arr = segment["arrival"]
                        carrier = segment["carrierCode"]
                        flight_num = segment["number"]
                        dep_date = date.fromisoformat(dep["at"][:10])
                        offers.append(
                            FlightOffer(
                                flight_number=f"{carrier}{flight_num}",
                                airline=carrier,
                                airline_code=carrier,
                                origin=dep["iataCode"],
                                destination=arr["iataCode"],
                                departure_date=dep_date,
                                departure_time=dep["at"][11:16],
                                arrival_time=arr["at"][11:16],
                                duration_minutes=_parse_duration(
                                    itinerary.get("duration", "PT0M")
                                ),
                                price=price,
                                currency=currency,
                                cabin_class=cabin_class,
                                source="amadeus",
                            )
                        )
            except (KeyError, ValueError):
                continue
        return offers
