from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AlertCreate(BaseModel):
    origin: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    destination: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    target_price: float = Field(gt=0)
    notify_channel: Literal["webhook"] = "webhook"
    notify_target: HttpUrl  # webhook URL，Pydantic 自动验证格式


class AlertResponse(BaseModel):
    id: int
    origin: str
    destination: str
    target_price: float
    notify_channel: str
    notify_target: str
    is_active: bool
    last_triggered_at: datetime | None
    created_at: datetime


class AlertsListResponse(BaseModel):
    alerts: list[AlertResponse]
