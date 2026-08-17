# 阶段四AI长期向量记忆 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 实现对话记忆自动入库、跨会话召回与双层记忆融合。

**Architecture:** 复用 Qdrant 与 Embedding 链路；chat 流结束后写记忆，请求前召回记忆并注入 Prompt。

**Tech Stack:** FastAPI + Qdrant + LiteLLM Embedding。

---

### Task 1: 配置与向量仓库

**Files:**
- Modify: `backend/app/core/config.py`、`.env.example`
- Modify: `backend/app/repositories/vector_repo.py`

**Step 1:** 增加 memory 配置。

**Step 2:** 增加 upsert/search/delete memory。

### Task 2: 记忆写入

**Files:**
- Modify: `backend/app/api/chat.py`

**Step 1:** 流结束后生成记忆文本并写入 Qdrant，异常仅 warning。

### Task 3: 记忆召回与 Prompt 融合

**Files:**
- Modify: `backend/app/services/chat_service.py`
- Modify: `backend/app/services/document_service.py`

**Step 1:** `stream_chat_events` 支持 `session_id` 并召回记忆。

**Step 2:** `build_rag_messages` 支持 `memories`。

### Task 4: 测试

**Files:**
- Modify: `backend/tests/test_rag.py`、`backend/tests/test_persistence.py`

**Step 1:** 增加记忆 Prompt 测试，chat 持久化测试 mock 记忆网络。

**Step 2:** `pytest -q`。

### Task 5: 容器实测

**Step 1:** 会话 A 说“我的名字是小明”，会话 B 问“我叫什么名字”，确认能跨会话召回。

**Step 2:** 检查 Qdrant `memory_vectors` 有记忆点。

### Task 6: 学习文档与归档

**Step 1:** 写 `docs/learning/阶段4/01~04`。

**Step 2:** 归档 + `pnpm harness:check`。
