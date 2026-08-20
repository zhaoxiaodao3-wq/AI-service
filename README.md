# AIGC 对话 + RAG + AI 记忆项目

一个从零搭建、重原理、重工程能力的个人 AIGC 项目。它不是为了做一个玩具 Demo，而是把一条真实的 AI 应用工程链路完整走一遍：多模型统一对接、流式聊天、业务数据持久化、自建 RAG 知识库、双层 AI 记忆、用户认证与多租户、Agent 工具调用、异步任务、缓存/限流/安全防护与日志观测。

如果别人拿到这个仓库，本 README 按“这是什么、结构怎样、从哪入手、如何启动”四件事组织。

## 1. 这是什么项目

一句话：一个带完整后端分层、自建知识库、长期记忆和多租户认证的 AI 对话应用。

核心能力：

| 能力 | 说明 |
|------|------|
| 多模型统一对接 | FastAPI + LiteLLM 封装，模型配置落库，支持双模式与按模型配置 |
| 流式对话 | SSE 逐段输出，聊天记录自动持久化，前端打字机效果 |
| RAG 知识库 | 文档上传、解析、切片、向量化、Qdrant 检索、混合检索 + RRF、Rerank 精排、引用溯源 |
| 双层 AI 记忆 | 会话内短期记忆 + 跨会话长期向量记忆 |
| 用户体系 | JWT 登录、刷新令牌、多租户数据隔离 |
| Agent 工具 | Function Calling 循环、工具注册与安全执行、天气/汇率等高级工具 |
| 异步任务 | Redis + RQ 异步处理文档，Worker 独立容器，前端展示进度 |
| 工程与安全 | 响应缓存、分布式限流、Prompt 注入/SSRF 防护、开源/免费模型 Guard 检测 |
| 可观测 | Docker 容器日志、Loki + Grafana 实时日志平台、Adminer/Qdrant 可视化 |

适合人群：

- 想系统了解 FastAPI 分层、RAG、Agent、工程化落地的新人。
- 需要一个 AI 对话项目作为学习样本、面试项目或二次开发基座的人。

## 2. 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router + Axios |
| 后端 | Python FastAPI + LiteLLM（二次封装）+ SQLAlchemy + Pydantic |
| 业务数据库 | PostgreSQL 16（Docker） |
| 向量数据库 | Qdrant（Docker 自建） |
| 缓存 / 队列 | Redis 7（Docker），RQ 异步任务 |
| 工具 | Docker Compose、pnpm、pytest |

## 3. 总体架构

```text
浏览器
  │ http://localhost:5173
  ▼
前端（Vue3 SPA，本地 pnpm dev 或 Nginx 容器）
  │ /api
  ▼
后端（FastAPI + LiteLLM）
  ├── PostgreSQL      业务数据（会话/消息/用户/模型配置/文档）
  ├── Qdrant          文档向量 + 记忆向量
  ├── Redis          缓存、分布式限流、RQ 任务队列
  ├── Worker         RQ 异步文档处理
  └── Loki + Grafana  容器日志实时观测
```

请求主链路：前端流式请求 → 后端 Guard 检查 → 多轮 Agent/工具（可选）→ 上下文组装（RAG/记忆检索）→ 模型调用 → SSE 流式返回并落库。

## 4. 目录结构

```text
D:\code\AI-agent\
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── adapters/           # 模型适配层（多模型/双模式封装）
│   │   ├── api/                # 路由层：chat、auth、documents、stats 等
│   │   ├── core/               # 配置、安全、限流、缓存
│   │   ├── db/                 # 数据库会话与初始化
│   │   ├── models/             # SQLAlchemy 实体
│   │   ├── repositories/       # 数据访问层
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务服务：聊天、RAG、记忆、Guard、文档、任务
│   │   ├── tools/              # Agent 工具注册与实现
│   │   └── utils/              # 通用工具
│   ├── scripts/                # worker、qdrant 初始化、模型下载脚本
│   ├── tests/                  # pytest 测试
│   ├── data/uploads/           # 上传文件目录（运行时）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # Vue3 + TS 前端
│   ├── src/
│   │   ├── api/                # 接口封装
│   │   ├── components/         # 公共组件
│   │   ├── layouts/            # 布局
│   │   ├── router/             # 路由与守卫
│   │   ├── views/              # 页面：登录、聊天、上传等
│   │   └── assets/
│   ├── Dockerfile + nginx 配置
│   └── package.json
├── docs/
│   ├── learning/               # 阶段 0-11 配套学习文档，按阶段目录组织
│   ├── superpowers/            # 需求/规格/计划/归档（Harness 管理）
│   └── interview/              # 面试知识点总结
├── observability/              # Loki/Grafana/Promtail 配置
├── scripts/                    # Harness 校验、目录初始化等工程脚本
├── docker-compose.yml          # 主编排：postgres/qdrant/redis/backend/worker/frontend
├── docker-compose.observability.yml  # Loki + Grafana + Promtail
├── docker-compose.tools.yml          # Adminer / Qdrant Dashboard 等工具
├── .env.example                # 根级 Docker 编排配置模板
├── AGENTS.md                   # 开发协作规范（Codex/Claude 等 Agent 读取）
└── package.json                # 根级脚本（harness:status / harness:check）
```

后端分层约定：`api -> services -> repositories -> models/db`，尽量让路由薄、业务进 service、数据访问进 repository，方便测试与替换实现。

## 5. 从哪里入手

推荐阅读顺序（新人版）：

1. 先读本 README，建立整体认知。
2. 读 `docs/learning/阶段0/` 的 7 篇基础文档，理解后端分层、Docker/PostgreSQL、Qdrant、FastAPI 接口、Vue 工程与联调方式。
3. 按阶段 1 到 11 的顺序读 `docs/learning/`，每个阶段都有配套“做了什么、为什么、命令解释、避坑”文档。
4. 需要改代码前，先读 `AGENTS.md` 和 `docs/superpowers/HARNESS_RULES.md`，了解目录规范与 Harness 门禁。
5. 看具体需求时，从 `docs/superpowers/v1.0.0/feature/<模块名>/` 的 `requirements -> specs -> plans -> archive` 顺序阅读，能完整还原一个功能从需求到交付的链路。

代码入口建议：

- 后端入口：`backend/app/main.py`，然后看 `backend/app/api/chat.py`、`backend/app/services/chat_service.py`。
- RAG 链路：`backend/app/services/retrieval_service.py`、`document_processing.py`。
- 安全 Guard：`backend/app/services/guard_service.py`、`security_service.py`。
- 前端入口：`frontend/src/router` 和 `frontend/src/views/ChatView.vue`。

## 6. 如何正常启动

### 6.1 前置条件

| 依赖 | 版本建议 |
|------|----------|
| Docker Desktop | 最新稳定版 |
| Node.js | >= 22 |
| pnpm | 随 Node 安装即可 |
| Python | >= 3.11（requirements 已兼容 3.14） |

### 6.2 第一次准备：复制并修改环境变量

根目录环境变量（Docker 编排用）：

```powershell
Copy-Item .env.example .env
```

后端环境变量（应用运行用）：

```powershell
cd backend
Copy-Item .env.example .env
cd ..
```

至少修改以下值：

- `POSTGRES_PASSWORD`：改成自己的强密码，两个 `.env` 保持一致。
- `SECRET_KEY`、`JWT_SECRET`：生产环境必须更换。
- `LLM_*`：填入你要用的模型服务信息；留空时聊天无法调用模型。
- `EMBEDDING_*`：RAG 需要的向量模型；开发期可设 `EMBEDDING_MODE=local` 用本地哈希向量。

`.env` 与 `backend/.env` 已被 gitignore，不要提交。

### 6.3 方式 A：Docker 一键启动（最省事）

```powershell
docker compose up -d --build
```

等待各容器 healthy 后访问：

- 前端：http://localhost:5173
- 后端健康检查：http://localhost:8000/api/health
- API 文档：http://localhost:8000/docs

### 6.4 方式 B：本地开发启动（适合改代码）

第一步，启动基础设施（PostgreSQL、Qdrant、Redis）：

```powershell
docker compose up -d postgres qdrant redis
docker compose ps
```

第二步，启动后端：

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.init_qdrant
uvicorn app.main:app --reload --port 8000
```

第三步（可选），启动异步 Worker（文档处理、RAG 任务）：

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m scripts.worker
```

第四步，启动前端：

```powershell
cd frontend
pnpm install
pnpm dev
```

访问 http://localhost:5173。

### 6.5 验证是否启动成功

```powershell
curl http://localhost:8000/api/health
docker compose ps
```

- 后端健康检查返回 `ok` 类响应。
- 前端页面能打开，注册/登录后能发起聊天。
- 上传文档后 Worker 日志能看到任务处理进度。

## 7. 测试与工程校验

后端测试：

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m pytest -q
```

前端构建校验：

```powershell
cd frontend
pnpm build
```

Harness 门禁（需求文档/模块结构校验）：

```powershell
pnpm harness:status
pnpm harness:check
```

提交前注意：先跑测试与构建，并确认 `.env`、上传文件等运行时产物未被提交。

## 8. 端口一览

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| PostgreSQL | localhost:5433（可在 .env 修改） |
| Qdrant | http://localhost:6333 |
| Grafana 观测界面 | http://localhost:3000 |
| Loki 日志服务 | localhost:3100 |
| Adminer 数据库管理 | http://localhost:5050 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## 9. 学习文档索引

| 文档 | 内容 |
|------|------|
| [01-FastAPI分层架构为什么这样拆](docs/learning/阶段0/01-FastAPI分层架构为什么这样拆.md) | 后端分层原理 |
| [02-Docker与PostgreSQL原理](docs/learning/阶段0/02-Docker与PostgreSQL原理.md) | 容器与数据库 |
| [03-Qdrant向量库原理](docs/learning/阶段0/03-Qdrant向量库原理.md) | 向量库原理 |
| [04-FastAPI接口与统一响应](docs/learning/阶段0/04-FastAPI接口与统一响应.md) | 接口与测试 |
| [05-Vue3工程结构说明](docs/learning/阶段0/05-Vue3工程结构说明.md) | 前端工程 |
| [06-前后端如何联调](docs/learning/阶段0/06-前后端如何联调.md) | 联调原理 |
| [07-多环境配置与密钥安全](docs/learning/阶段0/07-多环境配置与密钥安全.md) | 配置安全 |
| [07-Docker日志查看与请求响应链路](docs/learning/阶段1/07-Docker日志查看与请求响应链路.md) | 请求/响应日志与 Docker 查看 |
| [08-实时日志观测平台LokiGrafana](docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md) | Loki + Grafana 网页实时观测 |
| [09-阶段1补充对后续阶段影响](docs/learning/阶段1/09-阶段1补充对后续阶段影响.md) | 后续阶段任务影响与调整 |
| [01-业务数据建模与SQLAlchemy实体](docs/learning/阶段2/01-业务数据建模与SQLAlchemy实体.md) | 四张业务表与 ORM |
| [02-APIKey加密存储Fernet](docs/learning/阶段2/02-APIKey加密存储Fernet.md) | 敏感数据加密原理 |
| [03-会话消息CRUD与仓库服务分层](docs/learning/阶段2/03-会话消息CRUD与仓库服务分层.md) | 接口分层与 CRUD |
| [04-聊天流自动持久化与前端历史会话](docs/learning/阶段2/04-聊天流自动持久化与前端历史会话.md) | 消息自动落库与刷新恢复 |
| [05-Docker内建表与种子数据](docs/learning/阶段2/05-Docker内建表与种子数据.md) | 启动建表与幂等种子 |
| [01-RAG总览与文档解析](docs/learning/阶段3/01-RAG总览与文档解析.md) | RAG 五步法与文件解析 |
| [02-文本切片原理与实现](docs/learning/阶段3/02-文本切片原理与实现.md) | 切片窗口与重叠 |
| [03-Embedding与Qdrant入库](docs/learning/阶段3/03-Embedding与Qdrant入库.md) | 向量化与向量存储 |
| [04-相似度检索与RAGPrompt](docs/learning/阶段3/04-相似度检索与RAGPrompt.md) | 检索阈值与 Prompt 组装 |
| [05-前端上传与知识库问答联调](docs/learning/阶段3/05-前端上传与知识库问答联调.md) | 上传页与聊天开关 |
| [06-可视化查看数据库与向量库](docs/learning/阶段3/06-可视化查看数据库与向量库.md) | Adminer 与 Qdrant Dashboard |
| [01-长期记忆原理与双层记忆架构](docs/learning/阶段4/01-长期记忆原理与双层记忆架构.md) | 双层记忆架构 |
| [02-对话记忆自动入库](docs/learning/阶段4/02-对话记忆自动入库.md) | 记忆写入时机 |
| [03-跨会话检索与降噪](docs/learning/阶段4/03-跨会话检索与降噪.md) | 检索与阈值 |
| [04-记忆与知识库融合实测](docs/learning/阶段4/04-记忆与知识库融合实测.md) | 记忆+知识库融合 |
| [01-双模式兼容与按模型配置](docs/learning/阶段5/01-双模式兼容与按模型配置.md) | 模型表配置与回退 |
| [02-限流与流式重试](docs/learning/阶段5/02-限流与流式重试.md) | 限流与重试 |
| [03-模型调用统计](docs/learning/阶段5/03-模型调用统计.md) | 调用统计与 /api/stats |
| [04-工程化验收与运维建议](docs/learning/阶段5/04-工程化验收与运维建议.md) | 运维与验收 |
| [01-前端容器化与Nginx](docs/learning/阶段6/01-前端容器化与Nginx.md) | 前端镜像与 Nginx |
| [02-健康检查与一键部署](docs/learning/阶段6/02-健康检查与一键部署.md) | 健康检查与部署 |
| [03-项目收尾与运维清单](docs/learning/阶段6/03-项目收尾与运维清单.md) | 运维清单 |
| [04-二次元卡通风格改造](docs/learning/阶段6/04-二次元卡通风格改造.md) | 二次元 UI 改造 |
| [05-聊天布局与滚动交互优化](docs/learning/阶段6/05-聊天布局与滚动交互优化.md) | 布局与滚动交互 |
| [06-聊天布局审查与修订](docs/learning/阶段6/06-聊天布局审查与修订.md) | 布局审查与修订 |
| [01-认证架构与JWT](docs/learning/阶段7/01-认证架构与JWT.md) | JWT 认证 |
| [02-密码安全与刷新令牌](docs/learning/阶段7/02-密码安全与刷新令牌.md) | 密码与令牌 |
| [03-多租户数据隔离](docs/learning/阶段7/03-多租户数据隔离.md) | 数据隔离 |
| [04-前端登录与路由守卫](docs/learning/阶段7/04-前端登录与路由守卫.md) | 前端登录 |
| [01-FunctionCalling原理](docs/learning/阶段8/01-FunctionCalling原理.md) | Function Calling |
| [02-工具注册与安全执行](docs/learning/阶段8/02-工具注册与安全执行.md) | 工具注册与安全 |
| [03-Agent循环与前端展示](docs/learning/阶段8/03-Agent循环与前端展示.md) | Agent 循环 |
| [04-高级工具](docs/learning/阶段8/04-高级工具.md) | 天气与汇率工具 |
| [01-混合检索与RRF](docs/learning/阶段9/01-混合检索与RRF.md) | 混合检索与 RRF |
| [02-Rerank精排](docs/learning/阶段9/02-Rerank精排.md) | Rerank 精排 |
| [03-引用溯源与前端展示](docs/learning/阶段9/03-引用溯源与前端展示.md) | 引用溯源 |
| [01-异步任务与RQ](docs/learning/阶段10/01-异步任务与RQ.md) | Redis + RQ |
| [02-Worker容器与前端进度](docs/learning/阶段10/02-Worker容器与前端进度.md) | Worker 与进度 |
| [01-模型响应缓存](docs/learning/阶段11/01-模型响应缓存.md) | 响应缓存 |
| [02-分布式限流](docs/learning/阶段11/02-分布式限流.md) | 分布式限流 |
| [03-Prompt注入与SSRF防护](docs/learning/阶段11/03-Prompt注入与SSRF防护.md) | 安全防护 |
| [04-LLM安全防护增强](docs/learning/阶段11/04-LLM安全防护增强.md) | 多层安全防护 |
| [05-开源免费模型检测接入](docs/learning/阶段11/05-开源免费模型检测接入.md) | Guard Provider |
| [01-Alembic数据库迁移](docs/learning/阶段12/01-Alembic数据库迁移.md) | 数据库迁移 |
| [02-OpenTelemetry全链路观测](docs/learning/阶段12/02-OpenTelemetry全链路观测.md) | Trace 观测 |
| [03-CI-CD流水线与GHCR镜像](docs/learning/阶段12/03-CI-CD流水线与GHCR镜像.md) | CI/CD |
| [04-宝塔VPS生产部署](docs/learning/阶段12/04-宝塔VPS生产部署.md) | 生产部署 |
| [05-备份恢复与运维清单](docs/learning/阶段12/05-备份恢复与运维清单.md) | 备份运维 |
| [全项目面试知识点总结](docs/interview/全项目面试知识点总结.md) | 面试参考资料 |
| [深度知识点详解](docs/interview/深度知识点详解.md) | 面试深度讲解 |

## 10. 阶段规划

| 阶段 | 内容 | 状态 |
|------|------|------|
| 0 | 环境搭建与架构初始化 | 已完成 |
| 1 | 基础 AI 对话 + 多模型对接 + 短期记忆 | 已完成（含 UI 优化与实时日志观测） |
| 2 | 业务数据全持久化 | 已完成（会话/消息/模型配置全落库） |
| 3 | 自建 Qdrant + 完整 RAG 知识库 | 已完成 |
| 4 | AI 长期向量记忆 | 已完成 |
| 5 | 工程化完善 + 双模式兼容 | 已完成 |
| 6 | Docker 容器化部署 + 收尾 | 已完成 |
| 7 | 用户认证与多租户 | 已完成 |
| 8 | Agent 工具调用 | 已完成 |
| 9 | RAG 增强：Rerank + 混合检索 + 引用溯源 | 已完成 |
| 10 | 异步任务与文件处理 | 已完成 |
| 11 | 缓存、分布式限流与安全 | 已完成 |
| 12 | 可观测性与工程化部署 | 已完成 |
| 13 | 产品化体验 | 需求已登记，未开始 |

## 11. 常见问题

- PostgreSQL 端口被占用：改 `.env` 里的 `POSTGRES_PORT`，并同步修改 `backend/.env` 的 `DATABASE_URL`。
- Embedding 服务不可用：开发期把 `EMBEDDING_MODE=local`，RAG 仍可跑通全链路。
- 聊天调用模型失败：检查 `LLM_PROVIDER`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` 是否齐全，以及后端日志中的实际报错。
- 上传文档后一直处理中：确认 Worker 已启动（本地开发需单独 `python -m scripts.worker`，Docker 模式看 `aigc-worker` 是否 healthy）。
- Guard 检测策略：`PROMPT_GUARD_PROVIDER` 支持 `heuristic` / `llm_judge` / `prompt_guard`，模型相关 provider 需要额外配置，失败会自动降级为 safe，不影响聊天。
- 修改根目录结构或新增需求文档：先读 `AGENTS.md` 与 `docs/superpowers/HARNESS_RULES.md`，按 Harness 目录规范操作。
