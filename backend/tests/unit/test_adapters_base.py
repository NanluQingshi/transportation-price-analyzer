"""
adapters.base 数据类构造测试。
"""

from datetime import date

import pytest

from src.adapters.base import AirportInfo, FlightDataSource, FlightOffer


def test_flight_offer_construction():
    offer = FlightOffer(
        flight_number="CA1234",
        airline="Air China",
        airline_code="CA",
        origin="PEK",
        destination="SHA",
        departure_date=date(2026, 8, 1),
        departure_time="08:00",
        arrival_time="10:15",
        duration_minutes=135,
        price=680.0,
        currency="CNY",
        cabin_class="ECONOMY",
        source="amadeus",
    )
    assert offer.flight_number == "CA1234"
    assert offer.price == 680.0
    assert offer.departure_date == date(2026, 8, 1)


def test_airport_info_construction():
    airport = AirportInfo(
        iata_code="PEK",
        name="北京首都国际机场",
        city="北京",
        country="中国",
    )
    assert airport.iata_code == "PEK"
    assert airport.city == "北京"


def test_flight_data_source_is_abstract():
    """FlightDataSource 是抽象基类，不能直接实例化。"""
    with pytest.raises(TypeError):
        FlightDataSource()  # type: ignore[abstract]


def test_flight_offer_equality():
    """相同参数构造两次，dataclass 应相等。"""
    kwargs = dict(
        flight_number="MU5137",
        airline="China Eastern",
        airline_code="MU",
        origin="SHA",
        destination="PEK",
        departure_date=date(2026, 9, 1),
        departure_time="14:00",
        arrival_time="16:00",
        duration_minutes=120,
        price=550.0,
        currency="CNY",
        cabin_class="ECONOMY",
        source="amadeus",
    )
    assert FlightOffer(**kwargs) == FlightOffer(**kwargs)
