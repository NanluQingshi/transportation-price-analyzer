# Flight Price Analyzer — 项目上下文

> 本文件是 AI 协作的上下文锚点，规范优先写进此文件，不依赖聊天传递。

## 项目简介

机票价格分析平台。聚合多渠道机票价格数据，提供搜索、历史趋势可视化与 Claude Agent 智能分析能力。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端语言 | Python 3.12 |
| 后端框架 | FastAPI >= 0.110，异步模式 |
| ORM | SQLAlchemy 2.x（async） |
| 数据库 | PostgreSQL + TimescaleDB |
| 缓存 | Redis |
| 任务调度 | APScheduler |
| 依赖管理 | Poetry（唯一，禁止混用 pip/conda） |
| 数据源 | Amadeus Flight Offers API |
| Agent | Claude API Tool Use（claude-opus-4-7 / claude-haiku-4-5） |
| 前端语言 | TypeScript 5.x，strict 开启 |
| 前端框架 | React 18，函数式组件 + Hooks |
| 样式 | TailwindCSS + CSS Modules |
| 打包 | Rollup |
| 路由 | React Router v6 |
| 数据请求 | Axios + React Query |
| 状态管理 | Zustand（UI 状态）+ React Query（服务端状态） |
| 输入校验 | Zod（前端）/ Pydantic（后端） |
| 前端包管理 | pnpm（唯一，禁止混用 npm/yarn） |

## 目录约定

```
flight-price-analyzer/
├── backend/
│   ├── prompts/          # Prompt 模板（独立管理，不内嵌在业务代码）
│   ├── schemas/          # JSON Schema（输入输出校验与文档）
│   ├── fixtures/         # 回放数据、测试快照
│   └── src/
│       ├── api/          # 路由层（只做装配和参数校验）
│       ├── workflows/    # Agent 主流程（只做 orchestration）
│       ├── tools/        # Agent 工具封装
│       ├── adapters/     # 外部系统适配（Amadeus 等）
│       ├── services/     # 业务逻辑层
│       ├── parsers/      # 外部数据解析
│       ├── formatters/   # 输出格式化
│       ├── models/       # SQLAlchemy ORM 模型
│       ├── schemas/      # Pydantic 请求/响应模型
│       ├── scheduler/    # 定时任务
│       ├── cache/        # Redis 封装
│       └── db/           # 数据库连接
└── frontend/src/
    ├── components/       # 通用组件（PascalCase 目录）
    ├── pages/            # 页面（camelCase 目录）
    ├── hooks/            # 全局 hooks（use 前缀）
    ├── services/         # API 请求层
    ├── stores/           # Zustand 状态
    ├── types/            # 全局类型
    └── utils/            # 工具函数
```

## 编码规则

### 通用
- 每个模块只做一件事：路由层不含业务逻辑，服务层不含 HTTP 细节
- 命名表达业务语义，禁止 `temp`、`data2`、`handleIt` 等弱命名
- 注释只说"为什么"，不重复代码表面行为

### 后端
- 外部 API 调用只能在 `adapters/` 层，不散落在 service 或 api 层
- Agent 主流程（`workflows/`）只做编排，不直接写 HTTP 请求或 shell 命令
- Prompt 文件放 `prompts/`，禁止把大段 prompt 字符串写死在业务代码里
- 结构化输出必须经过 Pydantic schema 校验，不依赖自然语言文本作为系统接口
- 所有外部调用必须设置 timeout 和失败兜底，不吞错
- 定时任务必须幂等设计

### 前端
- 全部函数式组件，禁止 class component
- Props interface 独立导出，命名为 `XxxProps`，放在组件文件顶部
- 页面级请求统一走 React Query，不在组件内部直接 `useEffect` + `fetch`
- 受控组件统一用 `value / onChange`
- 单文件不超过 300 行，超出优先拆 hooks 或子组件

## 禁用项

- 禁止 `any` 类型（前端 TypeScript / 后端 mypy 均约束）
- 禁止把 API Key、token、密钥写入代码或默认配置文件，必须通过环境变量注入
- 禁止在 `api/` 路由层写业务逻辑
- 禁止在 `workflows/` 层直接写外部调用实现细节
- 禁止前端同时引入多套状态管理方案
- 禁止 `npm` 或 `yarn`（前端统一 pnpm）
- 禁止日志输出敏感信息（凭证、身份、token）

## 任务边界说明

- 单次任务控制在一个功能点内，大改动拆成多个可验证的小任务
- 涉及页面任务需说明：所在路由、组件边界、数据来源、交互行为
- 涉及 Agent 任务需说明：工具名称、输入输出 schema、失败策略

## 统一脚本入口

```bash
# 后端
uv run dev        # 启动开发服务器
uv run test       # 运行测试
uv run lint       # ruff + mypy
uv run migrate    # alembic upgrade head

# 前端
pnpm dev              # 启动开发服务器
pnpm build            # 构建生产包
pnpm test             # vitest
pnpm lint             # eslint + prettier
pnpm typecheck        # tsc --noEmit
```

## 相关文档

- [需求文档](docs/requirements.md)
- [技术选型](docs/tech-stack.md)
- [系统架构设计](docs/architecture.md)
- [编码规范](docs/coding-conventions.md)
- [开发计划](docs/roadmap.md)
- [工程规范](spec/)
