# 阶段零：环境搭建与架构初始化 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-13
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

完成 AIGC 项目阶段零地基：在 `D:\code\AI-agent` 下搭建 `backend/`（FastAPI 分层骨架 + PostgreSQL/Qdrant 连通 + 统一健康检查）与 `frontend/`（Vue3+TS 三页面骨架 + 路由/请求封装），Docker Compose 编排双数据库，建立多环境配置规范，并为 7 个步骤产出面向零基础学习者的原理文档。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `docker-compose.yml`、`.env.example`、`.gitignore`、`README.md` |
| 新增 | `backend/app/`（api/core/db/adapters 等分层骨架） |
| 新增 | `backend/scripts/init_qdrant.py`、`check_connections.py` |
| 新增 | `backend/tests/test_health.py` |
| 新增 | `frontend/src/`（router/layouts/views/api 等） |
| 新增 | `docs/learning/阶段0/01~07` 共 7 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段零环境搭建与架构初始化/`（requirements/spec/plans/archive） |

## 验收结果

### 后端

- [x] 后端可启动，`GET /api/health` 返回 200 与统一格式 JSON。
- [x] 分层目录齐全：api/core/models/schemas/services/adapters/repositories/utils。
- [x] 模型适配器占位文件存在，且定义了统一接口协议。
- [x] 未引入任何业务路由（对话、会话等）。
- [x] `pytest tests/test_health.py` 通过（1 passed）。

### 基础设施

- [x] `docker compose up -d` 后 PostgreSQL 与 Qdrant 均 healthy。
- [x] `python -m scripts.init_qdrant` 幂等创建两个 Collection。
- [x] `python -m scripts.check_connections` 输出 PG、Qdrant 均 ok。

### 前端

- [x] `pnpm dev` 可启动，首页/聊天/文档上传三个路由可跳转。
- [x] Element Plus 组件渲染正常，导航高亮正确。
- [x] `/api` 代理已配置，前端访问 `/api/health` 返回 200。
- [x] `pnpm build` 类型检查与打包通过。

### 学习文档

- [x] 7 篇文档全部存在且五小节齐全（做了什么/为什么/原理/命令解释/避坑）。
- [x] 术语均有解释，命令逐条讲解。
- [x] 按文档复现无卡点。

### 代码注释

- [x] 每个方法/函数有 docstring 或头部注释。
- [x] 每个独立逻辑代码块前有中文注释。
- [x] 不直观单行有行内注释。
- [x] 前端模板区块与 script 逻辑均有注释。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | N/A | 阶段 0 无业务数据接口，仅静态页面占位 |
| 常量/mock/真数据 | 通过 | 数据库/向量库地址统一来自 `backend/.env`（`config.py` 单例读取），前端 `VITE_API_BASE=/api` 统一代理 |
| 多入口 | N/A | 无 A/B 类或多入口业务，仅前端三页面共用 `MainLayout` |
| 失败/缺省 | 通过 | `/api/health` 对 PG/Qdrant 探测失败返回 `"error"` 字段而非抛异常；默认配置均有 `.env.example` 占位 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求（阶段 0 为工程搭建）。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告
- [x] commit 前 validate-harness 已跑

## 遗留风险

- Element Plus 全量引入导致前端打包体积偏大（阶段 5 改按需引入）。
- `fastapi.testclient` 有 Starlette 弃用警告，不影响功能（后续可切换 httpx2）。
- Qdrant `VECTOR_SIZE=1536` 为占位值，阶段 3 按实际 Embedding 模型调整。
- 本机 PostgreSQL 占用 5432，本项目使用宿主机 5433，`.env` 中已注明。
