# 阶段九RAG增强Rerank混合检索引用溯源 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 混合检索 + Rerank + 引用溯源。

**Architecture:** DocumentChunk 落 PG 支持关键词；retrieval_service RRF 融合；adapter.rerank 精排；SSE citations 到前端。

**Tech Stack:** FastAPI + PostgreSQL + Qdrant + SiliconFlow Rerank。

---

### Task 1: DocumentChunk 与上传落库

**Files:**
- Modify: `backend/app/models/entities.py`、`backend/app/repositories/document_repo.py`
- Modify: `backend/app/api/documents.py`

### Task 2: 关键词检索与检索服务

**Files:**
- Create: `backend/app/repositories/document_chunk_repo.py`
- Create: `backend/app/services/retrieval_service.py`

### Task 3: Rerank 适配

**Files:**
- Modify: `backend/app/adapters/model_adapter.py`
- Modify: `backend/app/core/config.py`、`.env.example`

### Task 4: chat 接入与 citations

**Files:**
- Modify: `backend/app/services/chat_service.py`

### Task 5: 前端引用展示

**Files:**
- Modify: `frontend/src/api/chatStream.ts`、`frontend/src/views/ChatView.vue`

### Task 6: 测试、容器实测、学习文档、归档

**Files:**
- Create: `backend/tests/test_retrieval.py`
- Create: `docs/learning/阶段9/01~03`
