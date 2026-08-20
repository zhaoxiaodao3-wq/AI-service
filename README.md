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

## 项目架构

```text
浏览器
  │ http://localhost:5173
  ▼
前端容器（Nginx，SPA + /api 代理）
  │ /api
  ▼
后端容器（FastAPI + LiteLLM）
  ├── PostgreSQL（业务数据）
  ├── Qdrant（文档向量 + 记忆向量）
  ├── Loki + Grafana（实时日志观测）
  └── Adminer / Qdrant Dashboard（可视化）
```

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

### 4. 通过 Docker 查看后端日志

```powershell
docker compose up -d --build backend   # 第一次构建并启动后端容器
docker compose logs -f backend          # 跟随查看请求/响应日志
```

日志实时输出到 stdout、不写文件：在聊天页发一条消息，`request start`、`request body`、`chat_stream start/finish`、`request end` 会立刻滚动出现，完整呈现前端请求与后端返回。详细说明见 [07-Docker日志查看与请求响应链路](docs/learning/阶段1/07-Docker日志查看与请求响应链路.md)。

### 5. 实时日志观测（Loki + Grafana）

```powershell
docker compose up -d --build   # 一键启动后端 + PostgreSQL + Qdrant + 观测栈
```

打开 http://localhost:3000，默认账号 `admin` / `admin`，进入 **Explore → Live tail** 即可在浏览器实时观测后端请求/响应日志（Promtail 从容器 stdout 实时采集，不写日志文件）。详细说明见 [08-实时日志观测平台LokiGrafana](docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md)。

### 6. 可视化查看数据库与向量库

- PostgreSQL 表：http://localhost:5050（Adminer，连接参数见 [06-可视化查看数据库与向量库](docs/learning/阶段3/06-可视化查看数据库与向量库.md)）
- Qdrant 向量库：http://localhost:6333/dashboard

## 端口一览

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
| [全项目面试知识点总结](docs/interview/全项目面试知识点总结.md) | 面试参考资料 |
| [深度知识点详解](docs/interview/深度知识点详解.md) | 面试深度讲解 |

## 阶段规划

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
| 12 | 可观测性与工程化部署 | 需求已登记，未开始 |
| 13 | 产品化体验 | 需求已登记，未开始 |
