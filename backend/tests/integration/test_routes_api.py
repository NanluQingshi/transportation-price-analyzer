"""
关注航线管理 API 集成测试。
使用 SQLite in-memory 数据库，不依赖真实 PostgreSQL。
"""

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
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
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


async def test_list_routes_empty(client: AsyncClient):
    res = await client.get("/api/routes")
    assert res.status_code == 200
    assert res.json()["routes"] == []


async def test_create_route(client: AsyncClient):
    res = await client.post("/api/routes", json={"origin": "PEK", "destination": "SHA"})
    assert res.status_code == 201
    data = res.json()
    assert data["origin"] == "PEK"
    assert data["destination"] == "SHA"
    assert data["is_active"] is True


async def test_create_route_invalid_iata(client: AsyncClient):
    res = await client.post("/api/routes", json={"origin": "pek", "destination": "SHA"})
    assert res.status_code == 422


async def test_list_routes_after_create(client: AsyncClient):
    await client.post("/api/routes", json={"origin": "PEK", "destination": "SHA"})
    await client.post("/api/routes", json={"origin": "SHA", "destination": "CAN"})
    res = await client.get("/api/routes")
    assert len(res.json()["routes"]) == 2


async def test_delete_route(client: AsyncClient):
    created = await client.post("/api/routes", json={"origin": "PEK", "destination": "CTU"})
    route_id = created.json()["id"]

    res = await client.delete(f"/api/routes/{route_id}")
    assert res.status_code == 204

    # 仍在列表中但标记为 inactive
    routes = await client.get("/api/routes")
    match = next(r for r in routes.json()["routes"] if r["id"] == route_id)
    assert match["is_active"] is False


async def test_delete_nonexistent_route(client: AsyncClient):
    res = await client.delete("/api/routes/99999")
    assert res.status_code == 404


async def test_create_duplicate_route_is_idempotent(client: AsyncClient):
    await client.post("/api/routes", json={"origin": "PEK", "destination": "SHA"})
    res2 = await client.post("/api/routes", json={"origin": "PEK", "destination": "SHA"})
    assert res2.status_code == 201  # 不报错

    routes = await client.get("/api/routes")
    pek_sha = [r for r in routes.json()["routes"] if r["origin"] == "PEK" and r["destination"] == "SHA"]
    assert len(pek_sha) == 1  # 不重复插入
