"""
GET /api/health 端点测试。
不 mock 数据库和 Redis，只验证响应结构（本地服务正常运行时 status 为 ok）。
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health_returns_200(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200


async def test_health_response_structure(client: AsyncClient):
    res = await client.get("/api/health")
    body = res.json()
    assert "status" in body
    assert "services" in body
    assert "database" in body["services"]
    assert "redis" in body["services"]


async def test_health_status_value(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.json()["status"] in ("ok", "degraded")


async def test_health_service_values(client: AsyncClient):
    res = await client.get("/api/health")
    for val in res.json()["services"].values():
        assert isinstance(val, str)
        assert len(val) > 0
