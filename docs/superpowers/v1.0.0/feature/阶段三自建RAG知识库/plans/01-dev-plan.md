# 阶段三自建RAG知识库 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 手写完成文档上传、切片、向量化、Qdrant 入库、检索与 RAG 流式问答。

**Architecture:** FastAPI 上传/文档接口 + 手写 chunker + LiteLLM Embedding + Qdrant 向量仓库 + 聊天流注入 RAG 上下文。

**Tech Stack:** FastAPI + SQLAlchemy + Qdrant + LiteLLM + Vue3 + Element Plus。

---

### Task 1: 配置与基础设施

**Files:**
- Modify: `backend/app/core/config.py`、`.env.example`、`backend/.env.example`
- Modify: `backend/app/db/qdrant.py`
- Modify: `backend/requirements.txt`（新增 `pypdf`）

**Step 1:** 增加 Embedding/RAG 配置项。

**Step 2:** Qdrant 集合按 `embedding_dimensions` 创建/重建。

### Task 2: 实体、切片、解析、向量仓库

**Files:**
- Modify: `backend/app/models/entities.py`（Document）
- Create: `backend/app/services/chunker.py`
- Create: `backend/app/services/document_service.py`
- Create: `backend/app/repositories/vector_repo.py`

**Step 1:** Document 表与 schema。

**Step 2:** 手写切片器、文件解析器。

**Step 3:** Qdrant 增删查仓库。

### Task 3: Embedding 与文档接口

**Files:**
- Modify: `backend/app/adapters/model_adapter.py`
- Create: `backend/app/api/documents.py`
- Modify: `backend/app/api/router.py`

**Step 1:** `embed_texts`。

**Step 2:** 上传/列表/删除接口。

### Task 4: RAG 问答

**Files:**
- Modify: `backend/app/schemas/chat.py`、`backend/app/services/chat_service.py`

**Step 1:** `use_rag` 检索并注入上下文。

### Task 5: 后端测试

**Files:**
- Create: `backend/tests/test_rag.py`

**Step 1:** chunker、RAG prompt、上传接口（mock）。

**Step 2:** `pytest -q`。

### Task 6: 前端

**Files:**
- Modify: `frontend/src/views/UploadView.vue`
- Modify: `frontend/src/views/ChatView.vue`、`frontend/src/api/chatStream.ts`

**Step 1:** 上传页上传/列表/删除。

**Step 2:** 聊天页知识库开关。

**Step 3:** `pnpm build`。

### Task 7: 容器实测与学习文档

**Step 1:** 重建 backend，真实上传 TXT 并知识库问答。

**Step 2:** 写 `docs/learning/阶段3/01~05` 学习文档。

**Step 3:** 归档 + `pnpm harness:check`。
