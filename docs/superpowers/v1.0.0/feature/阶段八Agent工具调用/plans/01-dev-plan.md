# 阶段八Agent工具调用 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** Function Calling 工具循环 + SSE 工具事件 + 前端开关。

**Architecture:** tools 注册中心 + 适配层 tool_calls + chat_service agent loop。

**Tech Stack:** FastAPI + LiteLLM + Vue3。

---

### Task 1: 工具层

**Files:**
- Create: `backend/app/tools/__init__.py`、`base.py`、`registry.py`、`builtin.py`

### Task 2: 适配层与 Agent 循环

**Files:**
- Modify: `backend/app/adapters/model_adapter.py`、`backend/app/services/chat_service.py`
- Modify: `backend/app/schemas/chat.py`、`backend/app/api/chat.py`

### Task 3: 前端

**Files:**
- Modify: `frontend/src/api/chatStream.ts`、`frontend/src/views/ChatView.vue`

### Task 4: 测试、容器实测、学习文档、归档

**Files:**
- Create: `backend/tests/test_tools.py`
- Create: `docs/learning/阶段8/01~03`
