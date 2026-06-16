from datetime import date

from src.services.flight_service import _cache_key


def test_cache_key_deterministic():
    key1 = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    key2 = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    assert key1 == key2


def test_cache_key_differs_by_route():
    k_pek_sha = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    k_pek_can = _cache_key("PEK", "CAN", date(2026, 7, 1), None, 1, "ECONOMY")
    assert k_pek_sha != k_pek_can


def test_cache_key_differs_by_date():
    k1 = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    k2 = _cache_key("PEK", "SHA", date(2026, 7, 2), None, 1, "ECONOMY")
    assert k1 != k2


def test_cache_key_differs_by_return_date():
    k_oneway = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    k_return = _cache_key("PEK", "SHA", date(2026, 7, 1), date(2026, 7, 5), 1, "ECONOMY")
    assert k_oneway != k_return


def test_cache_key_differs_by_cabin():
    k_eco = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    k_biz = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "BUSINESS")
    assert k_eco != k_biz


def test_cache_key_has_prefix():
    key = _cache_key("PEK", "SHA", date(2026, 7, 1), None, 1, "ECONOMY")
    assert key.startswith("search:")
