from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.alerts import AlertCreate, AlertResponse, AlertsListResponse
from src.services import alert_service

router = APIRouter()


@router.get("/alerts", response_model=AlertsListResponse)
async def list_alerts(db: AsyncSession = Depends(get_db)) -> AlertsListResponse:
    alerts = await alert_service.list_alerts(db)
    return AlertsListResponse(alerts=alerts)


@router.post("/alerts", response_model=AlertResponse, status_code=201)
async def create_alert(
    body: AlertCreate,
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    return await alert_service.create_alert(db, body)


@router.delete("/alerts/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await alert_service.delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
