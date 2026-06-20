"""
dashboard_service 纯逻辑单元测试（不依赖数据库）。
提取 trend 方向和涨跌幅计算逻辑进行验证。
"""

import pytest


def _compute_trend(today_price: float, yesterday_price: float | None) -> tuple[float, float, str]:
    """复现 dashboard_service.get_dashboard 中的涨跌计算逻辑。"""
    change = (today_price - yesterday_price) if yesterday_price else 0.0
    change_pct = (change / yesterday_price * 100) if yesterday_price else 0.0
    trend = "stable" if abs(change_pct) < 1 else ("up" if change > 0 else "down")
    return round(change, 2), round(change_pct, 1), trend


@pytest.mark.parametrize(
    "today,yesterday,expected_trend",
    [
        (700.0, 700.0, "stable"),       # 无变化
        (701.0, 700.0, "stable"),       # 涨幅 0.14%，在 1% 内
        (710.0, 700.0, "up"),           # 涨幅 1.43%
        (690.0, 700.0, "down"),         # 跌幅 1.43%
        (500.0, None, "stable"),        # 无昨日数据，当作不变
    ],
)
def test_trend_direction(today: float, yesterday: float | None, expected_trend: str):
    _, _, trend = _compute_trend(today, yesterday)
    assert trend == expected_trend


def test_price_change_calculation():
    change, pct, _ = _compute_trend(750.0, 700.0)
    assert change == 50.0
    assert pct == 7.1


def test_price_decrease_calculation():
    change, pct, _ = _compute_trend(630.0, 700.0)
    assert change == -70.0
    assert pct == -10.0


def test_no_yesterday_price():
    change, pct, trend = _compute_trend(500.0, None)
    assert change == 0.0
    assert pct == 0.0
    assert trend == "stable"


def test_stable_threshold_boundary():
    # 恰好 1% 变化应触发 up/down，不是 stable
    change, pct, trend = _compute_trend(707.0, 700.0)
    assert trend == "up"
    assert abs(pct) == pytest.approx(1.0, abs=0.1)
