"""
价格提醒服务。
check_and_notify 在每次快照任务完成后调用，对所有活跃提醒做价格检查。
通知渠道目前支持 webhook（可对接飞书/企微/Slack/自定义）。
"""

from datetime import UTC, datetime, timedelta

import httpx
import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.price_alert import PriceAlert
from src.models.price_snapshot import PriceSnapshot
from src.schemas.alerts import AlertCreate, AlertResponse

logger = structlog.get_logger(__name__)

# 同一条提醒 24 小时内最多触发一次，避免重复轰炸
_COOLDOWN_HOURS = 24


async def list_alerts(db: AsyncSession) -> list[AlertResponse]:
    result = await db.execute(select(PriceAlert).order_by(PriceAlert.id))
    return [_to_response(row) for row in result.scalars().all()]


async def create_alert(db: AsyncSession, body: AlertCreate) -> AlertResponse:
    alert = PriceAlert(
        origin=body.origin,
        destination=body.destination,
        target_price=body.target_price,
        notify_channel=body.notify_channel,
        notify_target=str(body.notify_target),  # HttpUrl → str
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    logger.info("alert_created", id=alert.id, origin=body.origin, destination=body.destination)
    return _to_response(alert)


async def delete_alert(db: AsyncSession, alert_id: int) -> bool:
    result = await db.execute(select(PriceAlert).where(PriceAlert.id == alert_id))
    row = result.scalar_one_or_none()
    if not row:
        return False
    row.is_active = False
    await db.commit()
    logger.info("alert_deactivated", id=alert_id)
    return True


async def check_and_notify() -> None:
    """检查所有活跃提醒，对触发条件的发送通知。由定时任务调用。"""
    log = logger.bind(job="alert_check")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)  # noqa: E712
        )
        alerts = result.scalars().all()

    if not alerts:
        return

    log.info("alert_check_started", count=len(alerts))
    triggered = 0

    for alert in alerts:
        if _in_cooldown(alert):
            continue

        current_price = await _get_current_min_price(alert.origin, alert.destination)
        if current_price is None or current_price > float(alert.target_price):
            continue

        success = await _send_notification(alert, current_price)
        if success:
            async with AsyncSessionLocal() as db:
                row = await db.get(PriceAlert, alert.id)
                if row:
                    row.last_triggered_at = datetime.now(UTC)
                    await db.commit()
            triggered += 1

    log.info("alert_check_finished", checked=len(alerts), triggered=triggered)


def _in_cooldown(alert: PriceAlert) -> bool:
    if alert.last_triggered_at is None:
        return False
    elapsed = datetime.now(UTC) - alert.last_triggered_at.replace(tzinfo=UTC)
    return elapsed < timedelta(hours=_COOLDOWN_HOURS)


async def _get_current_min_price(origin: str, destination: str) -> float | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.min(PriceSnapshot.price)).where(
                PriceSnapshot.origin == origin,
                PriceSnapshot.destination == destination,
                func.date(PriceSnapshot.captured_at) == func.current_date(),
            )
        )
    val = result.scalar()
    return float(val) if val is not None else None


async def _send_notification(alert: PriceAlert, current_price: float) -> bool:
    if alert.notify_channel == "webhook":
        return await _send_webhook(alert, current_price)
    logger.warning("unknown_notify_channel", channel=alert.notify_channel)
    return False


async def _send_webhook(alert: PriceAlert, current_price: float) -> bool:
    payload = {
        "type": "price_alert",
        "origin": alert.origin,
        "destination": alert.destination,
        "target_price": float(alert.target_price),
        "current_price": current_price,
        "currency": "CNY",
        "message": (
            f"✈️ 价格提醒：{alert.origin} → {alert.destination} "
            f"当前最低价 ¥{current_price:.0f}，"
            f"已低于你设定的目标价 ¥{float(alert.target_price):.0f}"
        ),
    }
    log = logger.bind(alert_id=alert.id, url=alert.notify_target[:40])
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(alert.notify_target, json=payload)
            resp.raise_for_status()
        log.info("webhook_sent", status=resp.status_code)
        return True
    except Exception as exc:
        log.error("webhook_failed", error=str(exc))
        return False


def _to_response(row: PriceAlert) -> AlertResponse:
    return AlertResponse(
        id=row.id,
        origin=row.origin,
        destination=row.destination,
        target_price=float(row.target_price),
        notify_channel=row.notify_channel,
        notify_target=row.notify_target,
        is_active=row.is_active,
        last_triggered_at=row.last_triggered_at,
        created_at=row.created_at,
    )
