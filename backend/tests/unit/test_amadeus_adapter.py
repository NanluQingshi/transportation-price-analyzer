from src.adapters.amadeus import _parse_duration


def test_parse_duration_hours_and_minutes():
    assert _parse_duration("PT2H15M") == 135


def test_parse_duration_hours_only():
    assert _parse_duration("PT3H") == 180


def test_parse_duration_minutes_only():
    assert _parse_duration("PT45M") == 45


def test_parse_duration_invalid_returns_zero():
    assert _parse_duration("") == 0
    assert _parse_duration("invalid") == 0


def test_parse_duration_zero():
    assert _parse_duration("PT0M") == 0
