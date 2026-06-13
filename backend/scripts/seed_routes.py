"""
预置热门关注航线。可重复执行（幂等），已存在的航线会跳过。

用法：
    uv run python scripts/seed_routes.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.dialects.postgresql import insert

from src.db.session import AsyncSessionLocal, engine, Base
from src.models.watched_route import WatchedRoute

ROUTES = [
    ("PEK", "SHA"),  # 北京 → 上海
    ("SHA", "PEK"),  # 上海 → 北京
    ("PEK", "CAN"),  # 北京 → 广州
    ("CAN", "PEK"),  # 广州 → 北京
    ("PEK", "CTU"),  # 北京 → 成都
    ("SHA", "CAN"),  # 上海 → 广州
    ("CAN", "SHA"),  # 广州 → 上海
    ("PEK", "SZX"),  # 北京 → 深圳
    ("SHA", "CTU"),  # 上海 → 成都
    ("PEK", "XIY"),  # 北京 → 西安
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        stmt = (
            insert(WatchedRoute)
            .values([{"origin": o, "destination": d} for o, d in ROUTES])
            .on_conflict_do_nothing(index_elements=["origin", "destination"])
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Inserted {result.rowcount} new routes (skipped existing).")
        print(f"Total configured: {len(ROUTES)} routes.")


if __name__ == "__main__":
    asyncio.run(main())
