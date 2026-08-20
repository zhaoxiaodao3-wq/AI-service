# 阶段十二可观测性与工程化部署 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 目标

生产可运维：数据库可迁移升级、全链路 Trace 可观测、CI 流水线一键构建推送、宝塔 VPS 生产部署与备份恢复可用。AI 完成全部代码/配置/文档，用户按文档完成账号/服务器/执行类操作。

## 设计

### Task A：Alembic 数据库迁移

- `backend/requirements.txt` 新增 `alembic>=1.13`。
- `backend/alembic/` 初始化（`alembic init` 形态），`alembic/env.py` 复用 `app.core.config` 的 `database_url` 与 `app.db.base.Base.metadata`，支持 sqlite 与 postgres 双数据库。
- 初始迁移 `0001_initial`：基于现有 `app/models/entities.py` 全量建表（users、chat_sessions、chat_messages、ai_models、documents、document_chunks、document_tasks、model_calls、refresh_tokens）。
- 启动改造：`app/db/init_db.py`（或等价入口）由 `create_all` 改为执行 `alembic upgrade head`（程序内调用 alembic API，容器启动自动迁移；保留 `python -m alembic upgrade head` 命令行方式）。
- 验证：sqlite 内存库 upgrade 建表成功、downgrade base 删表成功；不影响现有测试。

### Task B：OpenTelemetry 全链路 Trace

- `backend/requirements.txt` 新增：
  - `opentelemetry-sdk`
  - `opentelemetry-instrumentation-fastapi`
  - `opentelemetry-instrumentation-sqlalchemy`
  - `opentelemetry-instrumentation-httpx`
  - `opentelemetry-exporter-otlp`
- 新增 `backend/app/core/telemetry.py`：
  - OTLP exporter，endpoint 读 `OTEL_EXPORTER_OTLP_ENDPOINT`（默认 `http://tempo:4318`），服务名 `aigc-backend`。
  - FastAPI/SQLAlchemy/httpx 自动 instrumentation（幂等，可重复调用）。
  - `tracer()` 帮助函数 + LLM 手动 span（`llm.chat` 语义，含 model/usage 属性）与工具 span（`tool.execute`）。
  - 导出失败静默降级（try/except），不阻塞业务。
- `backend/app/main.py` 启动时调用 `setup_telemetry()`。
- LLM 调用点（`adapters/model_adapter.py` 的 chat/stream_chat）与工具执行点（`tools/registry.py` execute_tool）加手动 span。
- `docker-compose.observability.yml` 新增 `tempo` 服务（grafana/tempo:2.x，4317/4318/3200 端口）；Grafana provisioning 增加 Tempo datasource。

### Task C：CI 流水线（GitHub Actions + GHCR）

- 新增 `.github/workflows/ci.yml`：
  - Job `backend-test`：ubuntu-latest，Python 3.12，`pip install -r backend/requirements.txt`，`pytest -q`（无 Docker 依赖）。
  - Job `frontend-build`：Node 22，corepack pnpm，`pnpm install --frozen-lockfile`，`pnpm build`。
  - Job `docker-push`（分支 `main`、`master` push 时触发）：docker/build-push-action，构建 backend/frontend 镜像，推 `ghcr.io/${GITHUB_REPOSITORY_OWNER}/aigc-backend` 与 `aigc-frontend`，tag `latest` + 短 SHA；权限 `packages: write`（GHCR 用 GITHUB_TOKEN，无需手动 Secrets）。
- 前置确认：`frontend/pnpm-lock.yaml` 已跟踪、`backend/requirements.txt` 可离线安装。

### Task D：生产编排与备份（宝塔 VPS）

- 新增 `docker-compose.prod.yml`：
  - 服务：postgres/qdrant/redis/backend/worker/frontend（对齐现有 compose，镜像可选 `ghcr.io/...` 拉取或本地 build）。
  - 增加 `deploy.resources.limits`（cpu/memory）、日志轮转（`logging: max-size/max-file`）、`restart: unless-stopped`。
  - 端口收敛：仅暴露前端 `80:80`（HTTPS 由宝塔/nginx 处理），基础设施不对外映射。
  - 环境变量走 `.env.prod`（模板见 `.env.example`）。
- 新增 `scripts/backup.sh`（pg_dump + gzip + 时间戳 + 保留最近 N=7 份）与 `scripts/restore.sh`（按备份文件恢复），Windows 下不可执行但随仓库交付，宝塔计划任务挂 cron。

### Task E：学习文档（docs/learning/阶段12/，小白版，对齐阶段 11 标准）

1. `01-Alembic数据库迁移.md`
2. `02-OpenTelemetry全链路观测.md`
3. `03-CI-CD流水线与GHCR镜像.md`
4. `04-宝塔VPS生产部署.md`（含阿里云安全组、宝塔 Docker、SSL、反代）
5. `05-备份恢复与运维清单.md`

### Task F：交付物清单（用户操作部分）

- `docs/learning/阶段12/03` 含 GitHub 建库/push 步骤；`04` 含宝塔部署步骤；`05` 含备份恢复步骤。

## 验收标准

- [x] Alembic：`alembic upgrade head` 建表成功、`downgrade base` 可逆；容器启动自动迁移。
- [x] OTel：一次 HTTP 请求产生完整 Trace（Tempo 可见 HTTP→DB→Qdrant→LLM 子 span）；导出失败不影响业务。
- [x] CI：`.github/workflows/ci.yml` 语法正确、三个 Job 职责完整、GHCR 推送使用 GITHUB_TOKEN。
- [x] 生产编排：`docker-compose.prod.yml` `config` 校验通过、资源限制与日志轮转齐全。
- [x] 备份脚本：backup/restore 逻辑正确（含保留策略）。
- [x] 文档 5 篇齐全，含用户可执行的操作步骤。
- [x] 后端 `pytest -q` 通过；前端 `pnpm build` 通过（本机环境限制时注明验证方式）。
- [x] `pnpm harness:check` 无本模块警告。

## 非目标

- 不购买/配置云数据库（文档给出可选方案，默认容器 PG）。
- 不接入外部 APM（Sentry/Datadog），只做自建 Tempo/OTel。
- 不做多环境密钥管理（Vault），Secrets 走 GitHub Actions 注入。
- 不改动业务功能与前端界面。

## 风险

- 沙箱无 Docker 权限：prod 编排/OTel 实测需用户在宝塔/本机执行，文档覆盖验证命令。
- CI 首次运行时仓库需公开 Secrets 或 GHCR 匿名拉取权限：GHCR 用 GITHUB_TOKEN 规避。
- 测试在 CI 无 Redis/PG 环境下的行为：rate_limit/缓存均有降级路径，开发期验证。
