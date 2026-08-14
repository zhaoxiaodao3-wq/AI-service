# 阶段二业务数据全持久化 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 用户/模型/会话/消息全部落 PostgreSQL，前端历史会话刷新不丢，聊天自动保存。

**Architecture:** SQLAlchemy 实体 + 仓库/服务分层；FastAPI 会话 CRUD；SSE chat 携带 session_id 自动持久化；前端改用后端会话 API。

**Tech Stack:** FastAPI + SQLAlchemy + PostgreSQL + Vue3 + TypeScript。

---

### Task 1: 实体与初始化

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/models/entities.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/db/init_db.py`
- Modify: `backend/app/core/config.py`、`backend/app/main.py`、`.env.example`

**Step 1:** 定义四张表实体与 Base。

**Step 2:** 实现 Fernet 加密、建表与种子（默认用户 + 模型）。

**Step 3:** main.py 用 lifespan 调 `init_db()`。

### Task 2: 仓库/服务/接口

**Files:**
- Create: `backend/app/repositories/session_repo.py`、`message_repo.py`、`model_repo.py`、`user_repo.py`
- Create: `backend/app/services/session_service.py`、`message_service.py`、`model_service.py`
- Create: `backend/app/schemas/session.py`
- Create: `backend/app/api/sessions.py`
- Modify: `backend/app/api/router.py`、`backend/app/api/models.py`

**Step 1:** 实现会话/消息/模型仓库与服务。

**Step 2:** 实现会话 CRUD 与模型动态列表接口。

### Task 3: 聊天自动持久化

**Files:**
- Modify: `backend/app/schemas/chat.py`、`backend/app/api/chat.py`

**Step 1:** ChatStreamRequest 增加 session_id。

**Step 2:** 流前保存用户消息，流结束保存完整 AI 回复，错误保存错误文案。

### Task 4: 后端测试

**Files:**
- Create: `backend/tests/test_persistence.py`

**Step 1:** 用 SQLite 内存库覆盖会话 CRUD、消息查询、模型列表、chat 持久化。

**Step 2:** 运行 `pytest -q`。

### Task 5: 前端持久化

**Files:**
- Modify: `frontend/src/api/chatStream.ts`
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** chatStream 支持 sessionId。

**Step 2:** ChatView 改为后端会话：挂载加载/自动创建、切换加载消息、新建/重命名/删除。

**Step 3:** 运行 `pnpm build`。

### Task 6: 容器验证与归档

**Step 1:** 重建 backend 容器，curl 会话 CRUD 与聊天持久化。

**Step 2:** 写 archive，跑 `pnpm harness:check`。
