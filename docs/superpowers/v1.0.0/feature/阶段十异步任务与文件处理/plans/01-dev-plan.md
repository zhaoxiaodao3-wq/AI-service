# 阶段十异步任务与文件处理 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** Redis + RQ 异步处理文档上传。

**Architecture:** RQ 任务队列 + 共享上传卷 + worker 容器。

**Tech Stack:** Redis、RQ、FastAPI。

---

### Task 1: 配置与模型

**Files:**
- Modify: `backend/app/core/config.py`、`backend/requirements.txt`、`.env*`
- Modify: `backend/app/models/entities.py`（DocumentTask）
- Create: `backend/app/repositories/document_task_repo.py`

### Task 2: 任务处理与队列

**Files:**
- Create: `backend/app/services/document_processing.py`、`backend/app/services/task_queue.py`
- Create: `backend/scripts/worker.py`

### Task 3: 接口与前端

**Files:**
- Modify: `backend/app/api/documents.py`
- Modify: `frontend/src/views/UploadView.vue`

### Task 4: Compose

**Files:**
- Modify: `docker-compose.yml`

### Task 5: 测试、容器实测、学习文档、归档

**Files:**
- Create: `backend/tests/test_tasks.py`
- Create: `docs/learning/阶段10/01~02`
