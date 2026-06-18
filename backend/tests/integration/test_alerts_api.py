import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.session import Base, get_db
from src.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


VALID_ALERT = {
    "origin": "PEK",
    "destination": "SHA",
    "target_price": 500.0,
    "notify_channel": "webhook",
    "notify_target": "https://example.com/webhook",
}


async def test_list_alerts_empty(client: AsyncClient):
    res = await client.get("/api/alerts")
    assert res.status_code == 200
    assert res.json()["alerts"] == []


async def test_create_alert(client: AsyncClient):
    res = await client.post("/api/alerts", json=VALID_ALERT)
    assert res.status_code == 201
    data = res.json()
    assert data["origin"] == "PEK"
    assert data["target_price"] == 500.0
    assert data["is_active"] is True
    assert data["last_triggered_at"] is None


async def test_create_alert_invalid_iata(client: AsyncClient):
    bad = {**VALID_ALERT, "origin": "pk"}
    res = await client.post("/api/alerts", json=bad)
    assert res.status_code == 422


async def test_create_alert_invalid_url(client: AsyncClient):
    bad = {**VALID_ALERT, "notify_target": "not-a-url"}
    res = await client.post("/api/alerts", json=bad)
    assert res.status_code == 422


async def test_create_alert_negative_price(client: AsyncClient):
    bad = {**VALID_ALERT, "target_price": -100}
    res = await client.post("/api/alerts", json=bad)
    assert res.status_code == 422


async def test_list_alerts_after_create(client: AsyncClient):
    await client.post("/api/alerts", json=VALID_ALERT)
    await client.post("/api/alerts", json={**VALID_ALERT, "target_price": 800.0})
    res = await client.get("/api/alerts")
    assert len(res.json()["alerts"]) == 2


async def test_delete_alert(client: AsyncClient):
    created = await client.post("/api/alerts", json=VALID_ALERT)
    alert_id = created.json()["id"]

    res = await client.delete(f"/api/alerts/{alert_id}")
    assert res.status_code == 204

    alerts = await client.get("/api/alerts")
    match = next(a for a in alerts.json()["alerts"] if a["id"] == alert_id)
    assert match["is_active"] is False


async def test_delete_nonexistent_alert(client: AsyncClient):
    res = await client.delete("/api/alerts/99999")
    assert res.status_code == 404
