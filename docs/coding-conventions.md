# 编码规范

本文档是规范文件 `spec/02`、`spec/03`、`spec/05` 在本项目的落地执行细则。

---

## 1. 通用规范

### 模块职责

每个模块只做一件事，职责边界如下：

| 层 | 职责 | 禁止 |
|----|------|------|
| `api/` | 路由装配、参数校验、响应序列化 | 业务逻辑、数据库查询 |
| `services/` | 业务逻辑编排 | 直接 HTTP 请求、SQL 拼接 |
| `adapters/` | 外部系统调用（Amadeus 等） | 业务判断、数据持久化 |
| `workflows/` | Agent 流程编排 | 外部调用实现细节 |
| `tools/` | Agent 工具定义与调用入口 | 跨工具编排逻辑 |
| `parsers/` | 外部数据 → 内部模型转换 | 业务逻辑 |
| `formatters/` | 内部模型 → API 响应转换 | 数据获取 |

### 命名规范

- 名称表达业务语义：`flight_search_result` > `data`，`price_snapshot` > `item`
- 布尔变量用 `is_`/`has_`/`can_` 前缀：`is_cached`、`has_return_flight`
- 常量全大写下划线：`MAX_RETRY_COUNT`、`DEFAULT_CABIN_CLASS`

---

## 2. 后端（Python）规范

### 类型

- 所有函数参数和返回值必须有类型注解
- 使用 Pydantic v2 做请求/响应模型，不用裸 `dict`
- 禁止 `Any`（mypy strict 模式约束）
- 联合类型用 `X | Y`（Python 3.10+），不用 `Union[X, Y]`

```python
# 正确
async def search_flights(request: SearchRequest) -> SearchResponse:
    ...

# 错误
async def search_flights(request):
    ...
```

### 异步

- FastAPI 路由统一用 `async def`
- 数据库操作用 SQLAlchemy async session
- 并发调用多个适配器时用 `asyncio.gather`，不串行等待

### 外部调用

- 所有外部调用（Amadeus API、Claude API）必须设置 timeout
- 必须有明确的失败兜底，不吞 `Exception`
- 重试逻辑用 `tenacity` 库统一封装，不自写 retry 循环

```python
# 正确 — 统一 timeout + 重试
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def call_amadeus(params: AmadeusParams) -> AmadeusResponse:
    async with httpx.AsyncClient(timeout=10.0) as client:
        ...
```

### Agent 工具定义

每个工具文件结构：

```python
# tools/search_flights.py

TOOL_SCHEMA = {
    "name": "search_flights",
    "description": "...",
    "input_schema": { ... }   # JSON Schema，从 backend/schemas/ 引用
}

async def execute(args: SearchFlightsArgs) -> SearchFlightsResult:
    """工具执行入口，只做参数转发和结果返回，不含业务逻辑"""
    ...
```

### Prompt 管理

- Prompt 文件放 `backend/prompts/`，用 Markdown 格式
- 业务代码通过文件路径读取 prompt，不硬编码字符串
- Prompt 变更需同步更新 `fixtures/` 中对应的回放样例

### 日志

- 使用 `structlog` 输出结构化日志
- 日志字段：`task_id`、`step`、`tool`、`duration_ms`、`error`
- 禁止输出：API Key、用户搜索参数中的完整内容、token

---

## 3. 前端（TypeScript）规范

### 类型

- `tsconfig.json` 开启 `strict: true`
- 禁止 `any`，用 `unknown` + 类型收窄代替
- 常量用 `as const` + 联合字面量类型，不用 `enum`

```typescript
// 正确
const CABIN_CLASS = ['ECONOMY', 'BUSINESS', 'FIRST'] as const
type CabinClass = typeof CABIN_CLASS[number]

// 错误
enum CabinClass { ECONOMY, BUSINESS, FIRST }
```

### 组件规范

- 全部函数式组件，禁止 class component
- Props interface 独立导出，命名 `XxxProps`，放文件顶部
- 每个组件顶部一句话注释，说明解决什么问题
- 单文件不超过 300 行

```typescript
/** 航班价格趋势折线图，展示指定航线的历史价格波动 */
export interface PriceChartProps {
  /** 出发机场 IATA 代码 */
  origin: string
  /** 到达机场 IATA 代码 */
  destination: string
  /** 查询天数范围，默认 30 */
  days?: 30 | 90 | 180
}

export function PriceChart({ origin, destination, days = 30 }: PriceChartProps) {
  ...
}
```

### 数据请求

- 页面数据请求统一用 React Query 的 `useQuery` / `useMutation`
- 禁止在组件内用裸 `useEffect` + `fetch/axios` 管理异步状态
- API 调用封装在 `services/` 层，组件不直接引用 axios

```typescript
// 正确 — services/trendsApi.ts
export async function fetchPriceTrends(params: TrendsParams): Promise<TrendsResponse> {
  const { data } = await apiClient.get('/api/trends', { params })
  return trendsResponseSchema.parse(data)  // Zod 校验
}

// 正确 — pages/trends/hooks/usePriceTrends.ts
export function usePriceTrends(params: TrendsParams) {
  return useQuery({
    queryKey: ['trends', params],
    queryFn: () => fetchPriceTrends(params),
  })
}
```

### 输入校验

- 表单和 API 响应用 Zod schema 校验
- Schema 放 `src/types/` 目录，与类型定义放在一起

---

## 4. 质量卡口

### 提交前（自动执行）

```bash
# 后端
ruff check .         # lint
ruff format .        # format
mypy src/            # 类型检查
pytest tests/unit/   # 单元测试

# 前端
pnpm lint            # eslint + prettier
pnpm typecheck       # tsc --noEmit
pnpm test            # vitest
```

### Agent 变更专项检查

变更 `prompts/`、`tools/`、`workflows/` 时额外执行：

```bash
pytest tests/replay/   # 回放测试，确保输出结构未破坏
```

### 安全检查清单

- [ ] 无 API Key 硬编码
- [ ] 无 `any` 类型（CI mypy/tsc 自动拦截）
- [ ] 外部调用有 timeout 设置
- [ ] 定时任务幂等（重跑不产生重复数据）
- [ ] 日志无敏感信息输出

---

## 5. 观测性要求

- 每次外部 API 调用记录：`adapter`、`endpoint`、`duration_ms`、`status_code`
- Agent 每次工具调用记录：`tool_name`、`args_hash`（不记录完整参数）、`duration_ms`、`success`
- 定时任务记录：`job_name`、`started_at`、`finished_at`、`records_written`、`error`（如有）
