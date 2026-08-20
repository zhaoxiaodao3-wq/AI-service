# 阶段十一LLM安全防护增强 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 输入/内容侧多层防护 + 数据边界。

**Architecture:** guard_service 统一检测；各数据入口接入。

**Tech Stack:** FastAPI + 现有免费模型。

---

### Task 1: 安全服务

**Files:**
- Modify: `backend/app/services/security_service.py`
- Create: `backend/app/services/guard_service.py`
- Modify: `backend/app/core/config.py`、`.env*`

### Task 2: 内容侧接入

**Files:**
- Modify: `backend/app/services/document_processing.py`
- Modify: `backend/app/services/retrieval_service.py`
- Modify: `backend/app/tools/registry.py`
- Modify: `backend/app/services/document_service.py`

### Task 3: chat 与 guard

**Files:**
- Modify: `backend/app/services/chat_service.py`

### Task 4: 测试、容器实测、文档、归档

**Files:**
- Modify: `backend/tests/test_security.py`
- Create: `docs/learning/阶段11/04-LLM安全防护增强.md`
