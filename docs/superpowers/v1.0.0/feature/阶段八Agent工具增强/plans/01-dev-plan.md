# 阶段八Agent工具增强 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 增加天气与汇率两个免费实用工具。

**Architecture:** 在现有 tools/builtin.py 增加异步 HTTP 工具并注册。

**Tech Stack:** httpx + FastAPI tools。

---

### Task 1: 实现工具

**Files:**
- Modify: `backend/app/tools/builtin.py`、`backend/app/tools/registry.py`

### Task 2: 测试与文档

**Files:**
- Modify: `backend/tests/test_tools.py`
- Create: `docs/learning/阶段8/04-高级工具.md`

### Task 3: 容器实测、归档

**Step 1:** 重建 backend，聊天开启工具问天气/汇率。

**Step 2:** archive + `pnpm harness:check`。
