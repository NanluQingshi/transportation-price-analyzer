from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.trends import TrendsResponse
from src.services import trend_service

router = APIRouter()

DaysParam = Literal[30, 90, 180]


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    origin: str = Query(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"),
    destination: str = Query(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"),
    days: DaysParam = 30,
    db: AsyncSession = Depends(get_db),
) -> TrendsResponse:
    return await trend_service.get_trends(db, origin, destination, days)
