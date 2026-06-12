from datetime import date

from pydantic import BaseModel, Field, model_validator


class SearchRequest(BaseModel):
    origin: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    destination: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    departure_date: date
    return_date: date | None = None
    adults: int = Field(default=1, ge=1, le=9)
    cabin_class: str = Field(default="ECONOMY")

    @model_validator(mode="after")
    def validate_dates(self) -> "SearchRequest":
        if self.return_date and self.return_date < self.departure_date:
            raise ValueError("return_date must be after departure_date")
        return self


class FlightOfferResponse(BaseModel):
    flight_number: str
    airline: str
    airline_code: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    price: float
    currency: str
    cabin_class: str
    source: str


class SearchResponse(BaseModel):
    results: list[FlightOfferResponse]
    cached: bool
    query_time_ms: int


class AirportResponse(BaseModel):
    iata: str
    name: str
    city: str
    country: str


class AirportSearchResponse(BaseModel):
    airports: list[AirportResponse]
