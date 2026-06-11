# 技术选型文档

## 1. 数据源

### 主数据源：Amadeus Flight Offers API
- **理由**：官方航班数据，覆盖全球航线，有免费测试额度（每月 2000 次调用），支持实时价格查询和历史价格
- **文档**：https://developers.amadeus.com/self-service/category/flights
- **补充**：国内航线数据若 Amadeus 覆盖不足，后续可扩展爬虫模块（携程/去哪儿），通过统一数据源接口接入

---

## 2. 后端

### 框架：FastAPI
- **理由**：异步支持好（适合并发调用多个数据源），自动生成 OpenAPI 文档，性能优于 Flask，比 Django 更轻量
- **版本**：FastAPI >= 0.110

### 任务调度：APScheduler
- **理由**：轻量，无需独立部署，适合定时抓取价格快照任务

### 数据库：PostgreSQL + TimescaleDB 扩展
- **理由**：价格历史数据属于时序数据，TimescaleDB 对时序查询性能优化显著；PostgreSQL 本身稳定可靠
- **ORM**：SQLAlchemy 2.x（异步模式）

### 缓存：Redis
- **理由**：缓存搜索结果（相同搜索条件 5 分钟内复用），减少 API 调用次数

### AI Agent：Claude API（Tool Use）
- **理由**：原生工具调用能力强，无需引入 LangChain 等重型框架，保持架构简洁
- **模型**：claude-opus-4-7（能力强）/ claude-haiku-4-5（快速响应场景）

---

## 3. 前端

### 语言：TypeScript 5.x（strict 模式开启）
- **理由**：规范要求类型系统覆盖输入、输出、配置、内部模型；strict 模式消除隐性 any

### 框架：React 18
- **理由**：用户指定，生态成熟；全部使用函数式组件 + Hooks

### 样式：TailwindCSS + CSS Modules
- **理由**：Tailwind 负责原子化布局与间距，CSS Modules 负责组件私有样式隔离

### 打包：Rollup
- **理由**：用户指定

### 路由：React Router v6
- **理由**：规范推荐，与 React 18 集成稳定

### 图表：Recharts
- **理由**：基于 React 封装，与 React 集成无缝，API 简洁，适合折线图、柱状图等需求
- **备选**：ECharts（功能更强，但体积较大）

### 数据请求：Axios + React Query (TanStack Query)
- **理由**：规范推荐组合；React Query 统一管理请求状态、缓存与重试，避免在组件内分散实现；Axios 负责底层拦截器与统一错误处理

### 状态管理：Zustand
- **理由**：轻量，API 简单，适合本项目规模；全局异步状态交给 React Query，Zustand 只管本地 UI 状态

### 输入校验：Zod
- **理由**：规范要求输入参数、配置对象使用 zod 做校验；与 TypeScript 类型推断无缝集成

---

## 4. 部署

### 容器化：Docker + Docker Compose
- **理由**：一键启动所有服务（FastAPI + PostgreSQL + Redis），便于云服务器部署

### 反向代理：Nginx
- **理由**：静态资源托管 + API 反向代理，生产环境标配

---

## 5. 开发工具

| 工具 | 用途 |
|------|------|
| Poetry | Python 依赖管理（全仓库唯一包管理方式） |
| uv | 快速包安装（Poetry 后端） |
| pnpm | 前端包管理（全仓库唯一，禁止混用 npm/yarn） |
| ESLint + Prettier | 前端格式化与静态检查 |
| Ruff | Python 格式化与 lint（替代 Black + Flake8） |
| pytest | 后端单元/集成/回放测试 |
| Alembic | 数据库迁移 |
| mypy | Python 静态类型检查 |

### 统一脚本入口（规范要求）

```
后端：
  uv run dev        # 启动开发服务器
  uv run test       # 运行测试
  uv run lint       # 格式化 + 类型检查
  uv run migrate    # 运行数据库迁移

前端：
  pnpm dev              # 启动开发服务器
  pnpm build            # 构建生产包
  pnpm test             # 运行测试
  pnpm lint             # ESLint + Prettier 检查
  pnpm typecheck        # tsc --noEmit
```
