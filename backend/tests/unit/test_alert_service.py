from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from src.services.alert_service import _in_cooldown


def _make_alert(last_triggered_at: datetime | None) -> MagicMock:
    alert = MagicMock()
    alert.last_triggered_at = last_triggered_at
    return alert


def test_in_cooldown_never_triggered():
    alert = _make_alert(None)
    assert _in_cooldown(alert) is False


def test_in_cooldown_triggered_recently():
    recent = datetime.now(UTC) - timedelta(hours=12)
    alert = _make_alert(recent)
    assert _in_cooldown(alert) is True


def test_in_cooldown_triggered_over_24h_ago():
    old = datetime.now(UTC) - timedelta(hours=25)
    alert = _make_alert(old)
    assert _in_cooldown(alert) is False


def test_in_cooldown_exactly_at_boundary():
    # 恰好 24 小时前，仍在冷却期（< 24h 才算冷却，= 24h 已过）
    boundary = datetime.now(UTC) - timedelta(hours=24, seconds=1)
    alert = _make_alert(boundary)
    assert _in_cooldown(alert) is False
