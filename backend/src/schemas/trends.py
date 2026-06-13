from datetime import date

from pydantic import BaseModel


class PriceDataPoint(BaseModel):
    date: date
    min_price: float
    avg_price: float
    max_price: float
    currency: str


class PriceStats(BaseModel):
    historical_min: float
    historical_avg: float
    current_price: float | None
    # low | below_average | average | above_average | high
    price_level: str


class TrendsResponse(BaseModel):
    origin: str
    destination: str
    days: int
    data_points: list[PriceDataPoint]
    stats: PriceStats
