from datetime import date

from pydantic import BaseModel


class RouteSummary(BaseModel):
    origin: str
    destination: str
    origin_city: str
    destination_city: str
    min_price: float
    currency: str
    price_change: float
    price_change_pct: float
    trend: str  # "up" | "down" | "stable"


class DashboardResponse(BaseModel):
    date: date
    routes: list[RouteSummary]
