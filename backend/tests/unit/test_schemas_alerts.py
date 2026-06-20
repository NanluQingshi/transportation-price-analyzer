"""AlertCreate schema 校验。"""

import pytest
from pydantic import ValidationError

from src.schemas.alerts import AlertCreate


VALID = {
    "origin": "PEK",
    "destination": "SHA",
    "target_price": 500.0,
    "notify_channel": "webhook",
    "notify_target": "https://example.com/hook",
}


def test_alert_create_valid():
    a = AlertCreate(**VALID)
    assert a.origin == "PEK"
    assert a.target_price == 500.0


def test_alert_create_zero_price_rejected():
    with pytest.raises(ValidationError):
        AlertCreate(**{**VALID, "target_price": 0})


def test_alert_create_negative_price_rejected():
    with pytest.raises(ValidationError):
        AlertCreate(**{**VALID, "target_price": -100})


def test_alert_create_invalid_url_rejected():
    with pytest.raises(ValidationError):
        AlertCreate(**{**VALID, "notify_target": "not-a-url"})


def test_alert_create_invalid_iata_rejected():
    with pytest.raises(ValidationError):
        AlertCreate(**{**VALID, "origin": "pk"})


def test_alert_create_default_channel():
    a = AlertCreate(
        origin="PEK",
        destination="SHA",
        target_price=500.0,
        notify_target="https://example.com/hook",
    )
    assert a.notify_channel == "webhook"
