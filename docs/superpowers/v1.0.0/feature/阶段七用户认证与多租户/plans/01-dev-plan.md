# 阶段七用户认证与多租户 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** JWT 认证 + 刷新令牌 + 业务数据按用户隔离。

**Architecture:** FastAPI security + PyJWT + bcrypt + RefreshToken 表；前端 Token 拦截器与路由守卫。

**Tech Stack:** FastAPI + PyJWT + bcrypt + Vue3。

---

### Task 1: 配置、实体、安全

**Files:**
- Modify: `backend/app/core/config.py`、`.env.example`、`backend/requirements.txt`
- Modify: `backend/app/models/entities.py`（RefreshToken）
- Modify: `backend/app/core/security.py`（hash/verify password、JWT、refresh 管理）

### Task 2: 认证接口与依赖

**Files:**
- Create: `backend/app/schemas/auth.py`、`backend/app/api/auth.py`、`backend/app/api/deps.py`
- Modify: `backend/app/api/router.py`

### Task 3: 多租户隔离

**Files:**
- Modify: `backend/app/services/session_service.py`、`backend/app/services/document_service.py`、`backend/app/services/chat_service.py`
- Modify: `backend/app/api/sessions.py`、`backend/app/api/documents.py`、`backend/app/api/chat.py`

### Task 4: 测试

**Files:**
- Create: `backend/tests/test_auth.py`
- Modify: `backend/tests/test_persistence.py`、`backend/tests/test_rag.py`

### Task 5: 前端登录

**Files:**
- Create: `frontend/src/views/LoginView.vue`
- Modify: `frontend/src/router/index.ts`、`frontend/src/api/request.ts`、`frontend/src/layouts/MainLayout.vue`

### Task 6: 迁移脚本、学习文档、归档

**Files:**
- Create: `backend/scripts/migrate_local_data.py`
- Create: `docs/learning/阶段7/01~04`
