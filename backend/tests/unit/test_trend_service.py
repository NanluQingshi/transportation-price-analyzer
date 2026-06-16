from datetime import date

import pytest

from src.services.trend_service import _price_level


@pytest.mark.parametrize(
    "current,avg,expected",
    [
        (400.0, 500.0, "low"),           # -20% → low
        (460.0, 500.0, "below_average"), # -8%  → below_average
        (500.0, 500.0, "average"),       # 0%   → average
        (520.0, 500.0, "average"),       # +4%  → average（边界内）
        (560.0, 500.0, "above_average"), # +12% → above_average
        (620.0, 500.0, "high"),          # +24% → high
    ],
)
def test_price_level(current: float, avg: float, expected: str):
    assert _price_level(current, avg, 0.0) == expected


def test_price_level_zero_avg():
    # avg 为 0 时不应该抛异常
    assert _price_level(500.0, 0.0, 0.0) == "average"
