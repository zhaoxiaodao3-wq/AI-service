# 阶段一后端日志与Docker观测 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 让用户通过 Docker 客户端看到前端请求与后端响应日志，同时不改变现有接口行为。

**Architecture:** FastAPI ASGI 中间件统一记录 HTTP 请求/响应；chat 事件流内记录 SSE 事件统计；backend 新增 Docker 镜像与 compose 服务，日志经 stdout 被 Docker 采集。

**Tech Stack:** Python FastAPI + uvicorn + Docker Compose。

---

### Task 1: 请求/响应日志中间件

**Files:**
- Create: `backend/app/core/access_log.py`
- Modify: `backend/app/main.py`

**Step 1:** 新建 `RequestLogMiddleware`：
- 拦截 `http` scope，包装 `receive` 收集请求体，包装 `send` 统计 status/bytes。
- 请求开始日志：method/path/client/body 摘要。
- 请求结束日志：status/bytes/duration_ms。
- 摘要函数对 `/api/chat/stream` 输出 messages 数量、model、最后 user 内容前 80 字；其他 JSON body 前 120 字。

**Step 2:** `main.py` 注册中间件（在 CORS 之后、路由之前）。

### Task 2: SSE 流式日志

**Files:**
- Modify: `backend/app/api/chat.py`

**Step 1:** `chat_stream` 进入时记录 `chat_stream start messages=N model=... preview=...`。

**Step 2:** `event_stream` 内统计 delta/done/error 次数与总字符数，结束时记录 `chat_stream finish events={...} chars=N preview=...`；ModelError 与兜底异常分别记录 warning/exception。

### Task 3: 日志测试

**Files:**
- Create: `backend/tests/test_access_log.py`

**Step 1:** 用 `caplog` 断言：
- `GET /api/models` 产生 `app.access` 日志且含 `status=200`。
- mock 适配层后 `POST /api/chat/stream` 产生 `app.chat` 的 start/finish 日志。

**Step 2:** 运行：
```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
```
期望：原 11 个 + 新增全部通过。

### Task 4: 后端 Docker 化

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Modify: `docker-compose.yml`

**Step 1:** Dockerfile 使用 `python:3.12-slim`，安装 requirements，复制 app/scripts，`uvicorn app.main:app --host 0.0.0.0 --port 8000`。

**Step 2:** `.dockerignore` 排除 venv、__pycache__、`.env`、tests。

**Step 3:** compose 增加 `backend` 服务：`env_file: ./backend/.env`，environment 覆盖 `DATABASE_URL`（postgres:5432）与 `QDRANT_URL`（http://qdrant:6333），depends_on healthy，端口 8000。

**Step 4:** 验证：
```powershell
docker compose config
docker compose build backend
```
期望：配置合法、镜像构建成功。

### Task 5: 学习文档与 README

**Files:**
- Create: `docs/learning/阶段1/07-Docker日志查看与请求响应链路.md`
- Modify: `README.md`

**Step 1:** 学习文档包含：Docker Desktop 查看日志、`docker compose logs -f backend`、日志字段逐段解释、一条真实链路示例。

**Step 2:** README 增加“查看日志”小节，并把阶段表阶段 1 标记为已完成（含补充）。

### Task 6: 容器日志实测

**Files:**
- 运行验证：`docker compose up -d backend`

**Step 1:** 启动 backend 容器，`curl /api/health` 与 `curl /api/chat/stream`（无 Key 时走 error 分支）。

**Step 2:** `docker compose logs backend` 应看到 request 开始/结束与 chat_stream start/finish 日志。

**Step 3:** 验证后停止容器（避免与本地 8000 冲突），归档。
