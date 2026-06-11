from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class FlightOffer:
    flight_number: str
    airline: str
    airline_code: str
    origin: str
    destination: str
    departure_date: date
    departure_time: str
    arrival_time: str
    duration_minutes: int
    price: float
    currency: str
    cabin_class: str
    source: str


@dataclass
class AirportInfo:
    iata_code: str
    name: str
    city: str
    country: str


class FlightDataSource(ABC):
    """外部机票数据源的统一接口，所有适配器必须实现此接口。"""

    @abstractmethod
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date | None = None,
        adults: int = 1,
        cabin_class: str = "ECONOMY",
    ) -> list[FlightOffer]:
        """查询指定航线的机票报价。"""
        ...

    @abstractmethod
    async def search_airports(self, query: str) -> list[AirportInfo]:
        """按关键词搜索机场（自动补全用）。"""
        ...
