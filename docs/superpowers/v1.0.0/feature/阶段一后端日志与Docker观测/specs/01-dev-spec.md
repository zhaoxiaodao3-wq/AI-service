# 阶段一后端日志与Docker观测 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

用户希望通过 Docker 客户端直接看到“前端 → 后端请求、后端 → 前端响应”的完整链路。当前后端只在本地 uvicorn 终端输出少量日志，且没有进入 Docker Compose。本规格新增结构化请求/响应日志，并把后端容器化，使 `docker compose logs -f backend` 与 Docker Desktop 都能看到完整调用记录。

## 方案选型

- 推荐：FastAPI ASGI 中间件 + chat 流事件日志，输出到 stdout（Docker 默认采集），不引入日志平台。
- 备选：接入文件日志/Sentry/ELK。超出当前阶段，不采用。
- Docker：为 backend 新增镜像与 compose 服务；前端仍走本地 Vite（阶段 6 再全容器化）。

## 设计

### 1. 请求/响应日志中间件

新增 `backend/app/core/access_log.py`，实现 ASGI 中间件 `RequestLogMiddleware`：

- 请求开始日志：`method`、`path`、`client_ip`；请求体完整读取后单独输出摘要日志。
- 请求结束日志：`status`、`response_bytes`、`duration_ms`。
- 请求体摘要规则：
  - `/api/chat/stream`：`messages` 数量、`model`、最后一条 user 内容前 80 字。
  - 其他 JSON 请求：body 前 120 字；非 JSON/空请求：`body_bytes=N`。
- 日志名统一为 `app.access`，级别 INFO，不记录 API Key 等敏感字段。

### 2. SSE 流式对话日志

`backend/app/api/chat.py` 事件流内增加 `app.chat` 日志：

- 开始：`chat_stream start messages=N model=... preview=...`
- 模型错误：`chat_stream model error code=... message=...`
- 兜底异常：`chat_stream unexpected error` + 堆栈
- 结束：`chat_stream finish events={delta:..,done:..,error:..} chars=N preview=前80字`

### 3. Docker 化后端

- 新增 `backend/Dockerfile`：`python:3.12-slim`，安装 requirements，运行 uvicorn 0.0.0.0:8000。
- 新增 `backend/.dockerignore`：排除 venv、缓存、`.env`、测试。
- `docker-compose.yml` 增加 `backend` 服务：
  - `env_file: ./backend/.env`（保留本地 LLM Key 配置）
  - environment 覆盖 `DATABASE_URL`（`postgres:5432`）与 `QDRANT_URL`（`http://qdrant:6333`）
  - `depends_on` postgres/qdrant healthy，映射 `8000:8000`。
- 本地开发方式不变：仍可直接 `uvicorn app.main:app`。

### 4. 学习文档与 README

- 新增 `docs/learning/阶段1/07-Docker日志查看与请求响应链路.md`：
  - 如何用 Docker Desktop 查看 `aigc-backend` 日志。
  - `docker compose logs -f backend`、`docker compose ps` 等命令。
  - 一条真实请求日志字段逐段解释（请求开始、SSE 事件、请求结束）。
- README 增加“查看日志”小节与阶段表修正。

### 5. 测试

新增 `backend/tests/test_access_log.py`：

- 普通接口日志包含 `GET /api/models`、`status=200`。
- chat 接口日志包含 `chat_stream start messages=1` 与 `chat_stream finish`。

## 验收标准

- [x] `pytest -q` 全部通过（原 11 个 + 新增日志测试）。
- [x] 请求日志包含 method/path/client/status/duration/body 摘要。
- [x] chat SSE 日志包含 start/finish、事件统计、字符数、预览；错误场景记录错误码。
- [x] `docker compose config` 校验通过。
- [ ] backend 镜像可构建并健康启动（当前环境 Docker Hub 不可达，配置已就绪，待网络恢复后验证）。
- [x] 本地 uvicorn 启动方式与接口行为不变；本地真实联调已看到完整请求/响应日志。

## 非目标

- 不做日志持久化/日志平台/限流（阶段 5/6）。
- 不把前端容器化（阶段 6）。
- 不改变 SSE 协议与前端调用方式。
