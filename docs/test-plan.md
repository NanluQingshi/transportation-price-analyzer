# 测试计划

## 范围

覆盖整个项目的后端（Python/FastAPI）和前端（React/TypeScript），包括：

- 单元测试：纯函数、业务逻辑、类型/Schema 校验
- 集成测试：API 端点（In-Memory SQLite + 外部依赖 Mock）
- 组件测试：React 组件渲染与交互

---

## 后端测试

### 已有测试（45 个）

| 文件 | 描述 | 数量 |
|------|------|------|
| `unit/test_amadeus_adapter.py` | `_parse_duration` ISO 8601 解析 | 5 |
| `unit/test_alert_service.py` | `_in_cooldown` 冷却期逻辑 | 4 |
| `unit/test_flight_service.py` | `_cache_key` 唯一性与前缀 | 6 |
| `unit/test_formatters.py` | `format_flight_offer` / `format_airport` | 3 |
| `unit/test_schemas.py` | `SearchRequest` Pydantic 校验 | 5 |
| `unit/test_trend_service.py` | `_price_level` 五档分类 | 7 |
| `integration/test_routes_api.py` | 关注航线 CRUD + 幂等 | 7 |
| `integration/test_alerts_api.py` | 价格提醒 CRUD + 校验 | 8 |

### 新增测试目标

#### 单元测试

| 文件 | 测试内容 |
|------|---------|
| `unit/test_dashboard_unit.py` | 趋势方向（up/down/stable）、涨跌幅计算 |
| `unit/test_adapters_base.py` | `FlightOffer` / `AirportInfo` 数据类构造与字段 |
| `unit/test_schemas_routes.py` | `RouteCreate` 校验（IATA 格式） |
| `unit/test_schemas_alerts.py` | `AlertCreate` 校验（价格 > 0、有效 URL） |

#### 集成测试（SQLite in-memory + Mock）

| 文件 | 端点 | 覆盖场景 |
|------|------|---------|
| `integration/test_health_api.py` | `GET /api/health` | 返回 200，响应结构合法 |
| `integration/test_search_api.py` | `POST /api/search` `GET /api/airports` | 输入校验（422）、Mock 正常返回、数据源异常（502） |
| `integration/test_trends_api.py` | `GET /api/trends` | 参数校验、空数据返回、有数据返回统计 |
| `integration/test_dashboard_api.py` | `GET /api/dashboard` | 无数据返回空列表、有数据返回路线摘要 |

---

## 前端测试

### 已有测试（13 个）

| 文件 | 描述 | 数量 |
|------|------|------|
| `components/FlightCard/index.test.tsx` | 航班卡片渲染 | 6 |
| `components/PriceChart/index.test.tsx` | 图表空状态 / 有数据 | 2 |
| `pages/chat/components/ToolCallBadge.test.tsx` | 工具调用标签 | 5 |

### 新增测试目标

#### 组件测试

| 文件 | 测试内容 |
|------|---------|
| `components/Spinner/index.test.tsx` | 渲染、三种尺寸、aria-label |
| `components/PageSkeleton/index.test.tsx` | 渲染结构 |
| `components/ErrorBoundary/index.test.tsx` | 正常渲染子树、捕获错误展示降级 UI、重试恢复 |
| `components/Layout/index.test.tsx` | Logo、所有导航项、移动端汉堡菜单展开/收起 |
| `components/AirportInput/index.test.tsx` | 标签渲染、placeholder、输入 dispatch onChange |

#### 类型 / Schema 测试

| 文件 | 测试内容 |
|------|---------|
| `types/flight.test.ts` | `searchResponseSchema` / `trendsResponseSchema` / `dashboardResponseSchema` parse |
| `types/chat.test.ts` | `chatEventSchema` 各事件类型 parse / 非法结构报错 |
| `types/routes.test.ts` | `routesListResponseSchema` parse |
| `types/alerts.test.ts` | `alertsListResponseSchema` parse |

---

## 测试策略

### 外部依赖 Mock 原则

- Amadeus API → `unittest.mock.AsyncMock` patch `src.services.flight_service._amadeus`
- Redis → 不 mock，health 接口只验证结构而非具体 status
- Claude API → 不在自动测试中调用，Agent workflow 测试留给手动/回放测试

### 数据库策略

- 集成测试统一使用 SQLite in-memory，通过 `dependency_overrides[get_db]` 注入
- PostgreSQL 特有函数（`func.date()`）在 SQLite 下用等价写法验证

### 覆盖率目标

| 层次 | 目标 |
|------|------|
| 后端核心业务逻辑（services/formatters） | > 80% |
| API 端点（api/） | 所有端点至少 1 个正常路径 + 1 个错误路径 |
| 前端组件（components/） | 所有共用组件有渲染测试 |
| 前端类型（types/） | 所有 Zod schema 有 parse 测试 |

---

## 执行方式

```bash
# 后端（全量）
cd backend && make test
# 或分类
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# 前端（全量）
cd frontend && pnpm test --run
```

---

## 文件不删除承诺

本次测试过程中**禁止删除任何文件**。如发现冗余文件（如空占位文件），将在测试全部通过后统一列出供确认。
