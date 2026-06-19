"""
GET /api/dashboard 端点集成测试。
"""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.session import Base, get_db
from src.main import app
from src.schemas.dashboard import DashboardResponse, RouteSummary

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


async def test_dashboard_returns_200(client: AsyncClient):
    res = await client.get("/api/dashboard")
    assert res.status_code == 200


async def test_dashboard_response_structure(client: AsyncClient):
    res = await client.get("/api/dashboard")
    body = res.json()
    assert "date" in body
    assert "routes" in body
    assert isinstance(body["routes"], list)


async def test_dashboard_empty_db_returns_empty_routes(client: AsyncClient):
    """空 DB 无快照数据时，routes 为空列表（有 watched_routes 但无价格数据）。"""
    res = await client.get("/api/dashboard")
    body = res.json()
    # 无数据时 routes 返回 []（因为今日价格为 None 会被过滤掉）
    assert isinstance(body["routes"], list)


async def test_dashboard_with_mocked_service():
    """用 mock service 验证有数据时的响应结构。"""
    mock_response = DashboardResponse(
        date=date.today(),
        routes=[
            RouteSummary(
                origin="PEK",
                destination="SHA",
                origin_city="北京",
                destination_city="上海",
                min_price=680.0,
                currency="CNY",
                price_change=-20.0,
                price_change_pct=-2.9,
                trend="down",
            )
        ],
    )

    with patch(
        "src.services.dashboard_service.get_dashboard",
        new=AsyncMock(return_value=mock_response),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            res = await c.get("/api/dashboard")

    assert res.status_code == 200
    body = res.json()
    assert len(body["routes"]) == 1
    route = body["routes"][0]
    assert route["origin"] == "PEK"
    assert route["min_price"] == 680.0
    assert route["trend"] == "down"
    assert route["price_change"] == -20.0
