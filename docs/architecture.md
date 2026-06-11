# 系统架构设计文档

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                        用户浏览器                         │
│              React + TailwindCSS + Rollup                │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / REST
┌───────────────────────▼─────────────────────────────────┐
│                    Nginx 反向代理                          │
│          静态资源托管 + /api/* 转发到后端                   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI 后端                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  搜索模块    │  │  趋势模块    │  │   Agent 模块     │  │
│  │ /search     │  │ /trends     │  │  /chat (claude) │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         │                │                  │           │
│  ┌──────▼──────────────────────────────────▼────────┐   │
│  │               数据服务层 (Service Layer)            │   │
│  │  FlightDataService  │  PriceHistoryService        │   │
│  └──────┬──────────────────────────┬────────────────┘   │
│         │                          │                    │
│  ┌──────▼──────┐          ┌────────▼────────┐           │
│  │  数据源适配层 │          │   Redis 缓存     │           │
│  │ DataSource  │          │  搜索结果缓存     │           │
│  │ Interface   │          │  5分钟 TTL       │           │
│  └──────┬──────┘          └─────────────────┘           │
│         │                                               │
│  ┌──────▼─────────────────────────┐                     │
│  │   具体数据源实现                  │                     │
│  │  AmadeusSource │ (未来可扩展)     │                     │
│  └──────┬─────────────────────────┘                     │
│         │                                               │
│  ┌──────▼──────┐                                        │
│  │  APScheduler│  定时任务：每日价格快照抓取               │
│  └─────────────┘                                        │
└─────────────────────────────────┬───────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼──────┐    ┌───────────▼──────┐   ┌───────────▼──────┐
│  PostgreSQL     │    │  Amadeus API      │   │  Claude API       │
│  + TimescaleDB  │    │  (外部机票数据)    │   │  (Agent 推理)     │
│  价格历史存储    │    └──────────────────┘   └──────────────────┘
└────────────────┘
```

---

## 2. 数据流设计

### 2.1 用户搜索流程

```
用户输入搜索条件
      │
      ▼
前端发送 POST /api/search
      │
      ▼
FastAPI 接收请求，校验参数
      │
      ▼
检查 Redis 缓存（key = hash(搜索条件)）
      │
   命中? ──── 是 ────▶ 直接返回缓存结果
      │
      否
      │
      ▼
调用 AmadeusSource.search()
      │
      ▼
写入 Redis 缓存（TTL 5分钟）
写入 PostgreSQL 价格历史表（异步）
      │
      ▼
返回搜索结果给前端
```

### 2.2 定时价格快照流程

```
APScheduler 每日 00:00 触发
      │
      ▼
读取"关注航线"配置（预设热门航线列表）
      │
      ▼
并发调用 Amadeus API 查询各航线价格
      │
      ▼
批量写入 PostgreSQL price_snapshots 表
      │
      ▼
完成（记录日志）
```

### 2.3 Agent 对话流程

```
用户自然语言提问
      │
      ▼
POST /api/chat { message: "..." }
      │
      ▼
FastAPI 将消息传给 AgentService
      │
      ▼
调用 Claude API（带 Tool Use）
      │
      ▼
Claude 决策调用哪个工具:
  ├── search_flights(origin, dest, date)
  ├── get_price_trend(origin, dest, days)
  └── analyze_price(origin, dest, target_date)
      │
      ▼
后端执行工具，返回数据给 Claude
      │
      ▼
Claude 生成自然语言分析报告
      │
      ▼
返回给前端展示（流式输出）
```

---

## 3. 数据库 Schema

### 3.1 price_snapshots（价格快照表）
```sql
CREATE TABLE price_snapshots (
    id              BIGSERIAL,
    origin          VARCHAR(3)     NOT NULL,  -- 出发机场 IATA 代码
    destination     VARCHAR(3)     NOT NULL,  -- 到达机场 IATA 代码
    departure_date  DATE           NOT NULL,  -- 航班出发日期
    airline         VARCHAR(10),              -- 航空公司代码
    flight_number   VARCHAR(10),              -- 航班号
    price           NUMERIC(10,2)  NOT NULL,  -- 价格
    currency        VARCHAR(3)     NOT NULL DEFAULT 'CNY',
    cabin_class     VARCHAR(20),              -- 舱位等级
    source          VARCHAR(20)    NOT NULL,  -- 数据来源（amadeus/crawler）
    captured_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW(),  -- 抓取时间
    PRIMARY KEY (id, captured_at)
);

-- TimescaleDB 时序分区（按抓取时间）
SELECT create_hypertable('price_snapshots', 'captured_at');

-- 索引
CREATE INDEX idx_price_route ON price_snapshots (origin, destination, departure_date);
CREATE INDEX idx_price_captured ON price_snapshots (captured_at DESC);
```

### 3.2 watched_routes（关注航线配置表）
```sql
CREATE TABLE watched_routes (
    id          SERIAL PRIMARY KEY,
    origin      VARCHAR(3)  NOT NULL,
    destination VARCHAR(3)  NOT NULL,
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (origin, destination)
);
```

### 3.3 airports（机场信息表，静态数据）
```sql
CREATE TABLE airports (
    iata_code   VARCHAR(3)   PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    country     VARCHAR(100) NOT NULL,
    latitude    NUMERIC(8,5),
    longitude   NUMERIC(8,5)
);
```

---

## 4. API 接口设计

### 4.1 搜索接口

```
POST /api/search
Content-Type: application/json

Request:
{
  "origin": "PEK",
  "destination": "SHA",
  "departure_date": "2026-07-15",
  "return_date": "2026-07-20",   // 可选，往返
  "adults": 1,
  "cabin_class": "ECONOMY"       // ECONOMY | BUSINESS | FIRST
}

Response:
{
  "results": [
    {
      "flight_number": "CA1234",
      "airline": "Air China",
      "airline_code": "CA",
      "departure_time": "08:00",
      "arrival_time": "10:15",
      "duration": "2h15m",
      "price": 680.00,
      "currency": "CNY",
      "cabin_class": "ECONOMY",
      "source": "amadeus"
    }
  ],
  "cached": false,
  "query_time_ms": 1240
}
```

### 4.2 价格趋势接口

```
GET /api/trends?origin=PEK&destination=SHA&days=30

Response:
{
  "origin": "PEK",
  "destination": "SHA",
  "data_points": [
    {
      "date": "2026-05-10",
      "min_price": 560.00,
      "avg_price": 720.00,
      "max_price": 1200.00,
      "currency": "CNY"
    }
  ],
  "stats": {
    "historical_min": 480.00,
    "historical_avg": 710.00,
    "current_price": 680.00,
    "price_level": "below_average"  // low | below_average | average | above_average | high
  }
}
```

### 4.3 机场搜索（自动补全）

```
GET /api/airports?q=北京

Response:
{
  "airports": [
    { "iata": "PEK", "name": "北京首都国际机场", "city": "北京" },
    { "iata": "PKX", "name": "北京大兴国际机场", "city": "北京" }
  ]
}
```

### 4.4 Agent 对话接口

```
POST /api/chat
Content-Type: application/json

Request:
{
  "message": "下个月北京到上海什么时候最便宜？"
}

Response（流式 SSE）:
data: {"type": "tool_call", "tool": "search_flights", "args": {...}}
data: {"type": "tool_result", "data": {...}}
data: {"type": "text", "content": "根据当前数据分析..."}
data: {"type": "done"}
```

### 4.5 热门航线每日汇总

```
GET /api/dashboard

Response:
{
  "date": "2026-06-09",
  "routes": [
    {
      "origin": "PEK",
      "destination": "SHA",
      "min_price": 650.00,
      "price_change": -50.00,     // 相比昨日变化
      "price_change_pct": -7.1,
      "trend": "down"             // up | down | stable
    }
  ]
}
```

---

## 5. 目录结构（规划）

按规范 02 分层：后端遵循 Agent 项目结构，前端遵循前端附录结构。

```
flight-price-analyzer/
├── CLAUDE.md                    # 项目上下文文件（AI 协作规范要求）
│
├── backend/
│   ├── prompts/                 # Prompt 模板、规则片段、few-shot 示例
│   │   ├── system.md            # Agent 系统 prompt
│   │   └── tools/               # 各工具的 prompt 片段
│   ├── schemas/                 # 输入输出 JSON Schema（供校验与文档用）
│   │   ├── search_request.json
│   │   ├── search_response.json
│   │   └── chat_event.json
│   ├── fixtures/                # 回放数据、测试快照、样例输入
│   │   ├── amadeus_response.json
│   │   └── agent_chat_cases/
│   ├── src/
│   │   ├── api/                 # FastAPI 路由层（只做路由装配与参数校验）
│   │   │   ├── search.py
│   │   │   ├── trends.py
│   │   │   ├── chat.py
│   │   │   ├── airports.py
│   │   │   └── dashboard.py
│   │   ├── workflows/           # Agent 主流程编排（只做 orchestration）
│   │   │   └── flight_agent.py
│   │   ├── tools/               # Agent 工具封装层（定义 tool schema + 调用入口）
│   │   │   ├── search_flights.py
│   │   │   ├── get_price_trend.py
│   │   │   └── analyze_price.py
│   │   ├── adapters/            # 外部系统适配层（Amadeus、爬虫等）
│   │   │   ├── base.py          # 数据源抽象接口
│   │   │   └── amadeus.py
│   │   ├── services/            # 业务逻辑层（搜索、趋势、Dashboard）
│   │   │   ├── flight_service.py
│   │   │   ├── trend_service.py
│   │   │   └── dashboard_service.py
│   │   ├── parsers/             # 外部数据解析（Amadeus 响应 → 内部模型）
│   │   │   └── amadeus_parser.py
│   │   ├── formatters/          # 输出格式化（内部模型 → API 响应）
│   │   │   └── price_formatter.py
│   │   ├── models/              # SQLAlchemy ORM 模型
│   │   │   ├── price_snapshot.py
│   │   │   ├── watched_route.py
│   │   │   └── airport.py
│   │   ├── schemas/             # Pydantic 请求/响应模型（与顶层 JSON Schema 对应）
│   │   │   ├── search.py
│   │   │   ├── trends.py
│   │   │   └── chat.py
│   │   ├── scheduler/           # APScheduler 定时任务
│   │   │   └── price_snapshot_job.py
│   │   ├── cache/               # Redis 缓存封装
│   │   │   └── redis_client.py
│   │   ├── db/                  # 数据库连接与 session 管理
│   │   │   └── session.py
│   │   └── config.py            # 配置加载（从环境变量读取）
│   ├── migrations/              # Alembic 迁移文件
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── replay/              # 基于 fixtures 的回放测试
│   ├── scripts/                 # setup、seed、smoke test 脚本
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── assets/              # 图片、字体等静态资源
│   │   ├── components/          # 通用 UI 组件（PascalCase 目录）
│   │   │   ├── PriceChart/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── index.test.tsx
│   │   │   │   └── index.module.css
│   │   │   ├── FlightCard/
│   │   │   └── AirportInput/
│   │   ├── pages/               # 页面模块（camelCase 目录）
│   │   │   ├── dashboard/
│   │   │   │   ├── components/  # 页面私有组件
│   │   │   │   ├── hooks/
│   │   │   │   └── index.tsx
│   │   │   ├── search/
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   └── index.tsx
│   │   │   ├── trends/
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   └── index.tsx
│   │   │   └── chat/
│   │   │       ├── components/
│   │   │       ├── hooks/
│   │   │       └── index.tsx
│   │   ├── hooks/               # 全局通用 hooks（use 前缀）
│   │   ├── services/            # API 请求层（Axios 封装）
│   │   │   ├── searchApi.ts
│   │   │   ├── trendsApi.ts
│   │   │   └── chatApi.ts
│   │   ├── stores/              # 全局状态（Zustand）
│   │   ├── types/               # 全局类型定义
│   │   ├── utils/               # 工具函数
│   │   ├── router/              # React Router 路由配置
│   │   └── app.tsx
│   ├── public/
│   ├── rollup.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docs/                        # 规范、设计、协议文档
├── spec/                        # 工程规范文件
├── docker-compose.yml
├── nginx.conf
└── README.md
```
