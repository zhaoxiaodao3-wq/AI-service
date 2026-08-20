# 阶段十二可观测性与工程化部署 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 生产可运维——Alembic 迁移、OTel Trace、CI/CD、宝塔 VPS 部署与备份。

**Architecture:** 迁移走 Alembic 版本表；观测走 OTel SDK → Tempo；CI 走 GitHub Actions → GHCR；部署走 docker-compose.prod.yml + 备份脚本。

**Tech Stack:** Alembic、OpenTelemetry SDK、GitHub Actions、GHCR、Docker Compose、宝塔面板。

---

### Task 1: Alembic 迁移

**Files:**
- Modify: `backend/requirements.txt`（加 `alembic>=1.13`）
- Create: `backend/alembic.ini`、`backend/alembic/env.py`、`backend/alembic/script.py.mako`、`backend/alembic/versions/0001_initial.py`
- Modify: `backend/app/db/init_db.py`（create_all → alembic upgrade head）
- Modify: `backend/app/main.py` 或启动入口调用迁移

**Checks:** `alembic upgrade head` 在 sqlite 建表；`downgrade base` 可逆；`pytest -q` 通过。

### Task 2: OTel 全链路 Trace

**Files:**
- Modify: `backend/requirements.txt`（加 OTel 5 包）
- Create: `backend/app/core/telemetry.py`
- Modify: `backend/app/main.py`（setup_telemetry）、`backend/app/adapters/model_adapter.py`（LLM span）、`backend/app/tools/registry.py`（工具 span）
- Modify: `docker-compose.observability.yml`（加 tempo）、`observability/grafana/provisioning/datasources/*.yml`（Tempo datasource）

**Checks:** 应用启动不报错；span 导出失败不影响请求。

### Task 3: CI 流水线

**Files:**
- Create: `.github/workflows/ci.yml`（backend-test / frontend-build / docker-push 三 Job）
- Verify: `frontend/pnpm-lock.yaml` 已跟踪；backend 测试无 Docker 依赖

**Checks:** YAML 语法正确；`pnpm harness:check` 通过。

### Task 4: 生产编排与备份

**Files:**
- Create: `docker-compose.prod.yml`
- Create: `scripts/backup.sh`、`scripts/restore.sh`
- Create: `.env.prod.example`（模板）

**Checks:** `docker compose -f docker-compose.prod.yml config` 语法校验（沙箱内仅静态校验，实测由用户执行）。

### Task 5: 学习文档 5 篇

**Files:**
- Create: `docs/learning/阶段12/01~05` 共 5 篇（小白版，含用户操作步骤）

**Checks:** 覆盖 spec 验收项；步骤可照做。

### Task 6: 验证与归档

**Files:**
- Modify: `backend/tests/`（如需适配迁移）、`docs/superpowers/v1.0.0/feature/阶段十二可观测性与工程化部署/archive/`

**Checks:** `pytest -q`、`pnpm harness:status` → DELIVERED、`pnpm harness:check` 无警告。
