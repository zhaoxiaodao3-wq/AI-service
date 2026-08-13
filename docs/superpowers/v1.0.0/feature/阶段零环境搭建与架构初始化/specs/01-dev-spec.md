# 阶段零：环境搭建与架构初始化 · 开发规格

**Requirement:** [requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 1. 概述

本规格描述 AIGC 对话项目的阶段零实现方案：在仓库根目录 `D:\code\AI-agent` 下搭建可运行的前后端基础工程，部署 PostgreSQL 与 Qdrant 双数据库环境，建立多环境配置规范，并为每个步骤产出面向零基础学习者的解释文档。

本阶段只搭地基，不实现模型对话、业务 CRUD、RAG、记忆等业务能力。

## 2. 项目布局（硬约束）

前后端工程均位于当前仓库根目录 `D:\code\AI-agent` 下，禁止放在仓库外或子模块外：

```text
D:\code\AI-agent\
├── backend/               # FastAPI 后端（本阶段搭建）
├── frontend/              # Vue3 + TS 前端（本阶段搭建）
├── docs/
│   ├── superpowers/       # 需求/规格/计划/归档（Harness 管理）
│   └── learning/阶段0/     # 每步配套学习解释文档（本阶段硬性交付）
├── docker-compose.yml     # 本阶段编排 PostgreSQL + Qdrant
├── .env.example           # 根级示例配置（数据库/向量库/LLM 占位）
├── AGENTS.md
├── package.json           # 仅 harness 脚本
└── README.md
```

## 3. 设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 仓库形态 | 单仓库，`backend/` + `frontend/` 并列 | 结构直观，小白易理解，便于整体提交 |
| 后端环境 | Python venv + `requirements.txt` | 比 poetry/uv 少一层概念，先讲清依赖管理 |
| 前端包管理 | pnpm | 需求文档已约定；命令与 npm 基本一致 |
| 数据库 | PostgreSQL 16（Docker Compose） | 手册固定技术栈 |
| 向量库 | Qdrant（Docker Compose） | 手册固定技术栈，自建为核心学习点 |
| 配置管理 | `pydantic-settings` + `.env` | 类型安全、多环境清晰 |
| ORM | SQLAlchemy 2.x 声明式 | 阶段 0 仅建 engine/session，不建表 |
| 端口约定 | 后端 8000 / 前端 5173 / PG 5432 / Qdrant 6333 | 主流默认值，可在 .env 覆盖 |
| 前后端联调 | 前端 Vite 代理 `/api` → `http://localhost:8000` | 避免跨域配置复杂化 |

## 4. 架构设计

### 4.1 总体架构

```text
┌──────────────────────────────────────────────────────────┐
│                      浏览器（前端）                        │
│  Vue3 + TS + Element Plus + Vite 代理 /api               │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼───────────────────────────────┐
│                  FastAPI 后端（backend/）                  │
│  api 路由层 → services 服务层 → adapters 模型适配层(占位)   │
│  core 配置/日志/异常 → repositories(占位) → utils          │
└───────┬──────────────────────────────┬───────────────────┘
        │ SQLAlchemy                    │ qdrant-client
┌───────▼──────────┐        ┌──────────▼──────────┐
│  PostgreSQL 16   │        │  Qdrant             │
│  db: aigc_chat   │        │  document_vectors   │
│  (Docker)        │        │  memory_vectors     │
│                  │        │  (Docker)           │
└──────────────────┘        └─────────────────────┘
```

### 4.2 后端分层

```text
backend/
├── app/
│   ├── main.py            # FastAPI 实例、CORS、路由挂载
│   ├── api/               # 路由层
│   │   ├── health.py      # GET /api/health
│   │   └── router.py      # 汇总路由
│   ├── core/              # 配置、日志、异常、响应
│   │   ├── config.py      # pydantic-settings 读取 .env
│   │   ├── logging.py
│   │   ├── exceptions.py  # 统一异常类
│   │   └── response.py    # 统一 {code, message, data}
│   ├── models/            # SQLAlchemy 模型（阶段 2 使用，先留空目录）
│   ├── schemas/           # Pydantic 模型（阶段 1+ 使用）
│   ├── services/          # 服务层（阶段 1+ 使用）
│   ├── adapters/
│   │   └── model_adapter.py  # LiteLLM 二次封装占位（阶段 1 实现）
│   ├── repositories/      # 数据访问层（阶段 2 使用）
│   └── utils/
├── db/
│   ├── session.py         # engine + SessionLocal + get_db 依赖
│   └── qdrant.py          # qdrant-client 连接与集合初始化
├── scripts/
│   ├── init_qdrant.py     # 幂等创建两个 Collection
│   └── check_connections.py # 一键检查 PG + Qdrant 连通
├── tests/
│   └── test_health.py
├── requirements.txt
└── .env.example
```

### 4.3 前端结构

```text
frontend/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── api/
│   │   └── request.ts     # axios 封装：baseURL/超时/错误提示/Token 预留
│   ├── router/
│   │   └── index.ts       # /、/chat、/upload
│   ├── layouts/
│   │   └── MainLayout.vue # 顶部导航 + 内容区
│   ├── views/
│   │   ├── HomeView.vue   # 首页（入口导航）
│   │   ├── ChatView.vue   # 聊天页（静态容器占位）
│   │   └── UploadView.vue # 文档上传页（静态占位）
│   ├── stores/            # Pinia（阶段 1+ 使用，先留空）
│   ├── components/
│   └── utils/
├── .env.development       # VITE_API_BASE=/api
├── .env.production
├── vite.config.ts         # /api 代理到 http://localhost:8000
├── package.json
└── tsconfig.json
```

## 5. 数据流与接口契约

### 5.1 健康检查

`GET /api/health`

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "service": "aigc-backend",
    "time": "2026-08-12T15:00:00+08:00",
    "database": "ok",
    "qdrant": "ok"
  }
}
```

- 统一响应格式：`{ code, message, data }`；`code = 0` 表示成功，非 0 表示失败。
- `database` / `qdrant` 只做轻量连通探测（`SELECT 1` / Qdrant 集合列表），探测失败时该字段为 `"error"`，接口仍返回 200，便于定位基础设施问题。

### 5.2 配置契约

`backend/.env.example`：

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://aigc_user:change_me@localhost:5432/aigc_chat
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_DOC=document_vectors
QDRANT_COLLECTION_MEMORY=memory_vectors
LLM_PROVIDER=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_PROXY_BASE_URL=
LLM_PROXY_API_KEY=
```

- 真实 `.env` 不入库、不提交；`backend/.env.example` 提交。
- `docker-compose.yml` 中 PG 用户/密码/库名与 `DATABASE_URL` 保持一致。

## 6. 任务设计

### 6.1 后端基础搭建

- 初始化 `backend/` 分层目录。
- 安装依赖：`fastapi`、`uvicorn[standard]`、`litellm`、`sqlalchemy`、`psycopg[binary]`、`pydantic`、`pydantic-settings`、`python-dotenv`、`cryptography`、`python-multipart`、`qdrant-client`。
- 实现统一响应与异常中间件。
- 实现 `GET /api/health`。
- 创建 `adapters/model_adapter.py` 占位：定义 `chat()` / `stream_chat()` 统一接口协议与 `ModelError`，仅抛 `NotImplementedError` 或返回占位，不调用真实模型。

### 6.2 PostgreSQL 环境

- 根目录 `docker-compose.yml` 编写 PostgreSQL 16 服务：
  - `POSTGRES_DB=aigc_chat`
  - `POSTGRES_USER=aigc_user`
  - `POSTGRES_PASSWORD` 从根级 `.env` 读取（本地默认值 + 注释要求修改）
  - 挂载 named volume `pg_data`
  - 端口映射 `5432:5432`（可配置）
- `db/session.py` 使用 SQLAlchemy 2.x 创建 `engine` / `SessionLocal` / `get_db`。
- 连通检查：健康接口执行 `SELECT 1`；`scripts/check_connections.py` 可独立运行。

### 6.3 Qdrant 环境

- `docker-compose.yml` 增加 Qdrant 服务，挂载 `qdrant_data` volume，端口 `6333:6333`。
- `db/qdrant.py` 封装连接与幂等集合初始化。
- `scripts/init_qdrant.py` 创建 `document_vectors`、`memory_vectors` 两个 Collection；已存在则跳过（幂等）。
- 向量维度与距离度量在本阶段固定为占位配置（`size=1536, distance=Cosine`），阶段 3/4 可调整。

### 6.4 前端基础工程

- 在 `frontend/` 初始化 Vue3 + TS + Vite 工程（`pnpm create vite` 或等价脚手架）。
- 安装并配置 Element Plus、vue-router、axios、pinia。
- `src/api/request.ts` 封装：统一 `baseURL`（开发环境 `/api`）、超时、401 预留、错误提示。
- `vite.config.ts` 配置 `/api` 代理到 `http://localhost:8000`。
- 三个路由：`/`、`/chat`、`/upload`，使用 `MainLayout`。

### 6.5 基础页面骨架

- 首页：项目标题 + 「进入聊天」「进入文档上传」两个入口按钮。
- 聊天页：消息列表容器 + 输入框 + 发送按钮（静态，不接接口）。
- 上传页：上传占位区域（静态）。
- 三页均可路由跳转，导航高亮当前页。

### 6.6 配置与规范

- 根级 `.env.example` 与 `backend/.env.example`。
- `frontend/.env.development`、`.env.production`。
- `backend/.gitignore`、`frontend/.gitignore`（忽略 `.env`、`node_modules`、`__pycache__`、venv）。
- 根目录 `README.md`：项目简介、目录说明、启动步骤（Docker → 后端 → 前端）、学习文档索引。

### 6.7 学习解释文档（硬性交付）

每完成一个步骤，同步在 `docs/learning/阶段0/` 写一篇：

```text
01-FastAPI分层架构为什么这样拆.md
02-Docker与PostgreSQL原理.md
03-Qdrant向量库原理.md
04-Vue3工程结构说明.md
05-前后端如何联调.md
06-多环境配置与密钥安全.md
```

每篇固定包含：这一步做了什么 / 为什么要这么做 / 底层原理（类比+通俗）/ 关键命令逐条解释 / 常见问题与避坑。零基础读者按文档可独立复现。

### 6.8 代码注释规范（硬性交付）

所有后端/前端代码必须写清中文注释，阅读对象为零基础学习者：

- 方法/函数：docstring 或头部注释，说明做什么、入参、返回。
- 代码块：独立逻辑（连接配置、异常处理、循环、分支）前有注释说明做什么/为什么。
- 单行：魔法数字、复杂表达式、配置字段等不直观代码加行内注释。
- 前端：`<template>` 区块与 `<script>` 函数/响应式变量都要注释。
- 禁止无信息注释（如“设置变量”），必须解释目的与原理。

已交付文件（Task 2/3/4 产物）按本规范补注释后再进入后续开发。

## 7. 错误处理

- 统一异常中间件捕获未处理异常，返回 `{ code: 500, message: "服务器内部错误" }`，日志记录堆栈。
- 健康接口对 PG/Qdrant 探测失败不抛异常，返回对应 `"error"` 字段。
- 前端 axios 拦截器统一弹出错误提示（静态阶段仅封装，不接业务）。

## 8. 测试与验收

### 后端

- [ ] `uvicorn app.main:app --reload` 可启动。
- [ ] `GET /api/health` 返回统一格式，`database=ok`、`qdrant=ok`（容器启动后）。
- [ ] `pytest tests/test_health.py` 通过。

### 基础设施

- [ ] `docker compose up -d` 后 PG 与 Qdrant 均为 healthy。
- [ ] `python scripts/init_qdrant.py` 幂等创建两个 Collection。
- [ ] `python scripts/check_connections.py` 输出 PG、Qdrant 均连通。

### 前端

- [ ] `pnpm dev` 可启动，三个路由可跳转。
- [ ] Element Plus 组件渲染正常，导航高亮正确。
- [ ] `/api` 代理已配置（访问后端 health 可通）。

### 学习文档

- [ ] 6 篇文档全部存在且五小节齐全。
- [ ] 术语均有解释，命令逐条讲解。
- [ ] 按文档复现无卡点。

### 代码注释

- [ ] 每个方法/函数有 docstring 或头部注释。
- [ ] 每个独立逻辑代码块前有中文注释。
- [ ] 不直观单行有行内注释。
- [ ] 前端模板区块与 script 逻辑均有注释。

## 9. 不在本期范围

- 模型对话、SSE 流式、短期记忆（阶段 1）
- 用户/会话/消息 CRUD、APIKey 加密存储（阶段 2）
- 文件解析、切片、Embedding、检索（阶段 3）
- 长期记忆入库与召回（阶段 4）
- 限流、统计、日志系统（阶段 5）
- 全量容器化部署（阶段 6）
