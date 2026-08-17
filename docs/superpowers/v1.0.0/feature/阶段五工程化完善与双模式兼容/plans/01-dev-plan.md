# 阶段五工程化完善与双模式兼容 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 模型配置化、流式重试、聊天限流与调用统计。

**Architecture:** adapter 按模型读 DB 配置；ASGI 中间件限流；ModelCall 表统计；/api/stats 汇总。

**Tech Stack:** FastAPI + SQLAlchemy + Qdrant/Loki 复用。

---

### Task 1: 配置与实体

**Files:**
- Modify: `backend/app/core/config.py`、`.env.example`
- Modify: `backend/app/models/entities.py`

**Step 1:** 增加 retry/limit 配置。

**Step 2:** 新增 `ModelCall` 表。

### Task 2: 按模型配置与重试

**Files:**
- Modify: `backend/app/adapters/model_adapter.py`

**Step 1:** `_resolve_credentials(model_name)` 读 DB。

**Step 2:** `stream_chat` 未出内容时重试。

### Task 3: 限流中间件

**Files:**
- Create: `backend/app/core/rate_limit.py`
- Modify: `backend/app/main.py`

**Step 1:** chat 接口限流 429。

### Task 4: 统计

**Files:**
- Create: `backend/app/repositories/model_call_repo.py`
- Create: `backend/app/services/stats_service.py`
- Create: `backend/app/api/stats.py`
- Modify: `backend/app/api/router.py`、`backend/app/api/chat.py`

**Step 1:** 写入 ModelCall。

**Step 2:** GET /api/stats。

### Task 5: 测试

**Files:**
- Modify: `backend/tests/test_persistence.py`、`backend/tests/test_rag.py`

**Step 1:** stats API、模型配置回退测试。

**Step 2:** `pytest -q`。

### Task 6: 容器实测、学习文档、归档

**Step 1:** 重建 backend，聊天后看 /api/stats。

**Step 2:** 写 `docs/learning/阶段5/01~04`。

**Step 3:** 归档 + `pnpm harness:check`。
