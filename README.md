# AIGC 对话 + RAG + AI 记忆项目

纯练手、重原理、重工程能力的个人 AIGC 项目，主打：多 AI 大模型统一对接、自研完整 RAG 链路、双层 AI 记忆、完整工程架构。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue3 + TypeScript + Vite + Element Plus + Pinia |
| 后端 | Python FastAPI + LiteLLM（二次封装）+ SQLAlchemy |
| 业务数据库 | PostgreSQL 16（Docker） |
| 向量数据库 | Qdrant（Docker 自建） |
| 工具 | Docker Compose、pnpm |

## 目录结构

```text
D:\code\AI-agent\
├── backend/        # FastAPI 后端（分层架构）
├── frontend/       # Vue3 + TS 前端
├── docs/
│   ├── superpowers/   # 需求/规格/计划/归档（Harness 管理）
│   └── learning/阶段0/ # 每步配套学习解释文档
├── docker-compose.yml  # PostgreSQL + Qdrant 编排
├── .env.example        # 配置模板
└── README.md
```

## 快速启动

### 1. 启动数据库与向量库

```powershell
Copy-Item .env.example .env          # 第一次：生成本地配置
# 编辑 .env，把 POSTGRES_PASSWORD 改成自己的强密码
docker compose up -d
docker compose ps                    # 两个容器应为 healthy
```

> 本机若 5432 已被占用，在 `.env` 里把 `POSTGRES_PORT` 改成 5433，后端 `DATABASE_URL` 同步修改。

### 2. 启动后端

```powershell
cd backend
Copy-Item .env.example .env          # 第一次：与根级密码保持一致
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.init_qdrant        # 幂等创建 Qdrant 集合
uvicorn app.main:app --reload --port 8000
```

健康检查：http://localhost:8000/api/health

### 3. 启动前端

```powershell
cd frontend
pnpm install
pnpm dev
```

访问：http://localhost:5173

## 端口一览

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| PostgreSQL | localhost:5433（可在 .env 修改） |
| Qdrant | http://localhost:6333 |

## 学习文档索引

| 文档 | 内容 |
|------|------|
| [01-FastAPI分层架构为什么这样拆](docs/learning/阶段0/01-FastAPI分层架构为什么这样拆.md) | 后端分层原理 |
| [02-Docker与PostgreSQL原理](docs/learning/阶段0/02-Docker与PostgreSQL原理.md) | 容器与数据库 |
| [03-Qdrant向量库原理](docs/learning/阶段0/03-Qdrant向量库原理.md) | 向量库原理 |
| [04-FastAPI接口与统一响应](docs/learning/阶段0/04-FastAPI接口与统一响应.md) | 接口与测试 |
| [05-Vue3工程结构说明](docs/learning/阶段0/05-Vue3工程结构说明.md) | 前端工程 |
| [06-前后端如何联调](docs/learning/阶段0/06-前后端如何联调.md) | 联调原理 |
| [07-多环境配置与密钥安全](docs/learning/阶段0/07-多环境配置与密钥安全.md) | 配置安全 |

## 阶段规划

| 阶段 | 内容 | 状态 |
|------|------|------|
| 0 | 环境搭建与架构初始化 | 已完成 |
| 1 | 基础 AI 对话 + 多模型对接 + 短期记忆 | 未开始 |
| 2 | 业务数据全持久化 | 未开始 |
| 3 | 自建 Qdrant + 完整 RAG 知识库 | 未开始 |
| 4 | AI 长期向量记忆 | 未开始 |
| 5 | 工程化完善 + 双模式兼容 | 未开始 |
| 6 | Docker 容器化部署 + 收尾 | 未开始 |
