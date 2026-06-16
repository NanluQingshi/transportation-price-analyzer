from datetime import datetime

from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    origin: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    destination: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class RouteResponse(BaseModel):
    id: int
    origin: str
    destination: str
    is_active: bool
    created_at: datetime


class RoutesListResponse(BaseModel):
    routes: list[RouteResponse]
