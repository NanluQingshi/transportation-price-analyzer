"""
GET /api/trends 端点集成测试。
使用 SQLite in-memory + 预置价格快照数据。
注意：SQLite 不支持 BigInteger 自增，测试时需显式传 id。
"""

from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.session import Base, get_db
from src.main import app
from src.models.price_snapshot import PriceSnapshot

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# 使用 naive datetime，避免 SQLite timezone 字符串解析差异
_NOW = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
_YESTERDAY = _NOW - timedelta(days=1)
_TWO_DAYS_AGO = _NOW - timedelta(days=2)


@pytest.fixture
async def db_with_data():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # 显式设置 id，绕过 SQLite 不支持 BigInteger 自增的限制
        snapshots = [
            PriceSnapshot(id=1, origin="PEK", destination="SHA",
                          departure_date=_NOW.date(), price=680.0,
                          currency="CNY", source="amadeus", captured_at=_NOW),
            PriceSnapshot(id=2, origin="PEK", destination="SHA",
                          departure_date=_NOW.date(), price=720.0,
                          currency="CNY", source="amadeus", captured_at=_NOW),
            PriceSnapshot(id=3, origin="PEK", destination="SHA",
                          departure_date=_NOW.date(), price=750.0,
                          currency="CNY", source="amadeus", captured_at=_YESTERDAY),
            PriceSnapshot(id=4, origin="PEK", destination="SHA",
                          departure_date=_NOW.date(), price=600.0,
                          currency="CNY", source="amadeus", captured_at=_TWO_DAYS_AGO),
        ]
        session.add_all(snapshots)
        await session.commit()
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_with_data: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_with_data
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ── 输入校验 ─────────────────────────────────────────────────────────────────

async def test_trends_missing_params(client: AsyncClient):
    res = await client.get("/api/trends")
    assert res.status_code == 422


async def test_trends_invalid_iata(client: AsyncClient):
    res = await client.get("/api/trends", params={"origin": "pek", "destination": "SHA"})
    assert res.status_code == 422


async def test_trends_invalid_days(client: AsyncClient):
    res = await client.get("/api/trends", params={
        "origin": "PEK", "destination": "SHA", "days": 45
    })
    assert res.status_code == 422


# ── 正常返回 ─────────────────────────────────────────────────────────────────

async def test_trends_empty_route(client: AsyncClient):
    """没有历史数据的航线返回空 data_points 和零值统计。"""
    res = await client.get("/api/trends", params={
        "origin": "PEK", "destination": "CTU", "days": 30
    })
    assert res.status_code == 200
    body = res.json()
    assert body["data_points"] == []
    assert body["stats"]["historical_min"] == 0.0
    assert body["stats"]["current_price"] is None


async def test_trends_response_structure(client: AsyncClient):
    """返回结构包含所有必要字段。"""
    res = await client.get("/api/trends", params={
        "origin": "PEK", "destination": "SHA", "days": 30
    })
    assert res.status_code == 200
    body = res.json()
    assert body["origin"] == "PEK"
    assert body["destination"] == "SHA"
    assert body["days"] == 30
    assert "data_points" in body
    stats = body["stats"]
    for key in ("historical_min", "historical_avg", "current_price", "price_level"):
        assert key in stats


async def test_trends_valid_days_values(client: AsyncClient):
    for days in [30, 90, 180]:
        res = await client.get("/api/trends", params={
            "origin": "PEK", "destination": "SHA", "days": days
        })
        assert res.status_code == 200, f"days={days} 应为有效值"


async def test_trends_price_level_is_valid_enum(client: AsyncClient):
    res = await client.get("/api/trends", params={
        "origin": "PEK", "destination": "SHA", "days": 30
    })
    body = res.json()
    if body["stats"]["current_price"] is not None:
        assert body["stats"]["price_level"] in (
            "low", "below_average", "average", "above_average", "high"
        )
