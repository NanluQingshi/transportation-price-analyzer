from datetime import date

from src.adapters.base import AirportInfo, FlightOffer
from src.formatters.price_formatter import format_airport, format_flight_offer


def _make_offer(**kwargs) -> FlightOffer:  # type: ignore[type-arg]
    defaults = dict(
        flight_number="CA1234",
        airline="Air China",
        airline_code="CA",
        origin="PEK",
        destination="SHA",
        departure_date=date(2026, 7, 1),
        departure_time="08:00",
        arrival_time="10:15",
        duration_minutes=135,
        price=680.0,
        currency="CNY",
        cabin_class="ECONOMY",
        source="amadeus",
    )
    defaults.update(kwargs)
    return FlightOffer(**defaults)


def test_format_flight_offer_basic():
    offer = _make_offer()
    result = format_flight_offer(offer)
    assert result.flight_number == "CA1234"
    assert result.price == 680.0
    assert result.currency == "CNY"
    assert result.source == "amadeus"


def test_format_flight_offer_preserves_all_fields():
    offer = _make_offer(price=1200.5, cabin_class="BUSINESS", duration_minutes=90)
    result = format_flight_offer(offer)
    assert result.price == 1200.5
    assert result.cabin_class == "BUSINESS"
    assert result.duration_minutes == 90


def test_format_airport_basic():
    info = AirportInfo(iata_code="PEK", name="北京首都国际机场", city="北京", country="中国")
    result = format_airport(info)
    assert result.iata == "PEK"
    assert result.city == "北京"
    assert result.country == "中国"
