import asyncio

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.services.snapshot_service import run_daily_snapshot

logger = structlog.get_logger(__name__)


def _run_snapshot_sync() -> None:
    """APScheduler 同步回调包装，在当前事件循环里 schedule 协程。"""
    asyncio.ensure_future(run_daily_snapshot())


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _run_snapshot_sync,
        trigger=CronTrigger(hour=1, minute=0),  # 每天凌晨 1:00 抓取
        id="daily_price_snapshot",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    logger.info("scheduler_configured", jobs=["daily_price_snapshot"])
    return scheduler
