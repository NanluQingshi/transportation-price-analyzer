"""
POST /api/search 和 GET /api/airports 端点集成测试。
外部调用（Amadeus + Redis）通过 mock 隔离。
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.adapters.base import AirportInfo, FlightOffer
from src.main import app

TOMORROW = (date.today().isoformat()[:-2] + str(date.today().day + 1).zfill(2))

_MOCK_OFFERS = [
    FlightOffer(
        flight_number="CA1234",
        airline="Air China",
        airline_code="CA",
        origin="PEK",
        destination="SHA",
        departure_date=date.today(),
        departure_time="08:00",
        arrival_time="10:15",
        duration_minutes=135,
        price=680.0,
        currency="CNY",
        cabin_class="ECONOMY",
        source="amadeus",
    )
]

_MOCK_AIRPORTS = [
    AirportInfo(iata_code="PEK", name="北京首都国际机场", city="北京", country="中国"),
    AirportInfo(iata_code="PKX", name="北京大兴国际机场", city="北京", country="中国"),
]


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── 输入校验 ──────────────────────────────────────────────────────────────────

async def test_search_missing_required_fields(client: AsyncClient):
    res = await client.post("/api/search", json={})
    assert res.status_code == 422


async def test_search_lowercase_iata_rejected(client: AsyncClient):
    res = await client.post("/api/search", json={
        "origin": "pek", "destination": "SHA", "departure_date": "2026-08-01"
    })
    assert res.status_code == 422


async def test_search_invalid_date_format(client: AsyncClient):
    res = await client.post("/api/search", json={
        "origin": "PEK", "destination": "SHA", "departure_date": "not-a-date"
    })
    assert res.status_code == 422


async def test_search_return_before_departure_rejected(client: AsyncClient):
    res = await client.post("/api/search", json={
        "origin": "PEK",
        "destination": "SHA",
        "departure_date": "2026-08-05",
        "return_date": "2026-08-01",
    })
    assert res.status_code == 422


async def test_search_adults_out_of_range(client: AsyncClient):
    res = await client.post("/api/search", json={
        "origin": "PEK", "destination": "SHA",
        "departure_date": "2026-08-01", "adults": 0,
    })
    assert res.status_code == 422


# ── 正常搜索（mock Amadeus + Redis）─────────────────────────────────────────

async def test_search_success(client: AsyncClient):
    with (
        patch("src.services.flight_service._amadeus") as mock_amadeus,
        patch("src.services.flight_service.cache_get", new=AsyncMock(return_value=None)),
        patch("src.services.flight_service.cache_set", new=AsyncMock()),
    ):
        mock_amadeus.search_flights = AsyncMock(return_value=_MOCK_OFFERS)
        res = await client.post("/api/search", json={
            "origin": "PEK",
            "destination": "SHA",
            "departure_date": "2026-08-01",
        })

    assert res.status_code == 200
    body = res.json()
    assert "results" in body
    assert "cached" in body
    assert "query_time_ms" in body
    assert len(body["results"]) == 1
    assert body["results"][0]["flight_number"] == "CA1234"
    assert body["cached"] is False


async def test_search_cache_hit(client: AsyncClient):
    cached_data = [
        {
            "flight_number": "MU5137", "airline": "China Eastern", "airline_code": "MU",
            "origin": "PEK", "destination": "SHA", "departure_date": "2026-08-01",
            "departure_time": "14:00", "arrival_time": "16:00", "duration_minutes": 120,
            "price": 550.0, "currency": "CNY", "cabin_class": "ECONOMY", "source": "amadeus",
        }
    ]
    with patch("src.services.flight_service.cache_get", new=AsyncMock(return_value=cached_data)):
        res = await client.post("/api/search", json={
            "origin": "PEK", "destination": "SHA", "departure_date": "2026-08-01",
        })

    assert res.status_code == 200
    body = res.json()
    assert body["cached"] is True
    assert body["query_time_ms"] == 0


async def test_search_amadeus_error_returns_502(client: AsyncClient):
    from amadeus import ResponseError
    with (
        patch("src.services.flight_service._amadeus") as mock_amadeus,
        patch("src.services.flight_service.cache_get", new=AsyncMock(return_value=None)),
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_amadeus.search_flights = AsyncMock(
            side_effect=ResponseError(mock_resp)
        )
        res = await client.post("/api/search", json={
            "origin": "PEK", "destination": "SHA", "departure_date": "2026-08-01",
        })

    assert res.status_code == 502


# ── 机场搜索 ────────────────────────────────────────────────────────────────

async def test_airports_missing_query(client: AsyncClient):
    res = await client.get("/api/airports")
    assert res.status_code == 422


async def test_airports_query_too_short(client: AsyncClient):
    res = await client.get("/api/airports", params={"q": "P"})
    assert res.status_code == 422


async def test_airports_success(client: AsyncClient):
    with patch("src.services.flight_service._amadeus") as mock_amadeus:
        mock_amadeus.search_airports = AsyncMock(return_value=_MOCK_AIRPORTS)
        res = await client.get("/api/airports", params={"q": "北京"})

    assert res.status_code == 200
    body = res.json()
    assert "airports" in body
    assert len(body["airports"]) == 2
    assert body["airports"][0]["iata"] == "PEK"


async def test_airports_returns_empty_list(client: AsyncClient):
    with patch("src.services.flight_service._amadeus") as mock_amadeus:
        mock_amadeus.search_airports = AsyncMock(return_value=[])
        res = await client.get("/api/airports", params={"q": "zzz"})

    assert res.status_code == 200
    assert res.json()["airports"] == []
