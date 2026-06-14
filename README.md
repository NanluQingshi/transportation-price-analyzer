# 机票价格分析平台

聚合多渠道机票价格，提供搜索、历史趋势可视化与 Claude Agent 智能分析能力。

## 功能

- **每日价格汇总** — Dashboard 展示关注航线当日最低价及涨跌情况
- **机票搜索** — 按出发地、目的地、日期搜索，支持城市名/机场代码自动补全
- **价格趋势** — 30/90/180 天历史折线图，标注历史最低、均价、当前价格位置
- **智能分析** — 对话式 AI 助手，自动调用搜索和趋势工具，给出购票建议

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · Redis |
| AI | Claude API (claude-opus-4-7) · Tool Use · SSE 流式输出 |
| 数据源 | Amadeus Flight Offers API |
| 前端 | React 18 · TypeScript · TailwindCSS · Rollup · Recharts |

## 本地开发

### 前置条件

- Python 3.12+、[uv](https://docs.astral.sh/uv/)
- Node.js 20+、pnpm
- PostgreSQL、Redis（本地运行）

### 后端

```bash
cd backend

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 AMADEUS_CLIENT_ID、AMADEUS_CLIENT_SECRET、ANTHROPIC_API_KEY

# 建库
psql postgres -c "CREATE DATABASE flight_analyzer;"

# 建表
make migrate

# 预置关注航线
uv run python scripts/seed_routes.py

# 启动开发服务器（http://localhost:8000）
make dev
```

### 前端

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发构建（watch 模式）
pnpm dev
```

用 Nginx 或直接打开 `frontend/public/index.html`（需引用 `dist/` 产物）访问页面。

### 一键验证

```bash
# 后端健康检查
curl http://localhost:8000/api/health

# 手动触发价格快照（需填好 Amadeus Key）
cd backend && uv run python -c "
import asyncio
from src.services.snapshot_service import run_daily_snapshot
asyncio.run(run_daily_snapshot())
"
```

## 生产部署（Docker）

```bash
# 复制并填写生产环境变量
cp .env.production.example .env.production

# 启动所有服务
docker compose up -d

# 建表（首次部署）
docker compose exec backend uv run alembic upgrade head

# 预置关注航线（首次部署）
docker compose exec backend uv run python scripts/seed_routes.py
```

服务启动后访问 `http://服务器IP`。

## 项目结构

```
flight-price-analyzer/
├── backend/
│   ├── prompts/          # Prompt 模板（独立管理）
│   ├── scripts/          # 一次性运维脚本
│   └── src/
│       ├── api/          # FastAPI 路由
│       ├── workflows/    # Agent 编排
│       ├── tools/        # Agent 工具
│       ├── adapters/     # 外部数据源
│       ├── services/     # 业务逻辑
│       ├── parsers/      # 数据解析
│       ├── formatters/   # 输出格式化
│       ├── models/       # ORM 模型
│       └── schemas/      # Pydantic 模型
└── frontend/src/
    ├── components/       # 通用组件
    ├── pages/            # 页面
    ├── services/         # API 请求层
    └── types/            # 类型定义
```

## 开发规范

见 [`docs/`](docs/) 和 [`spec/`](spec/)。
