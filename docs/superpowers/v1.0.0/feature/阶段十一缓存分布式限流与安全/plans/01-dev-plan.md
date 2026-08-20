# 阶段十一缓存分布式限流与安全 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** Redis 缓存 + 分布式限流 + 注入/SSRF 防护。

**Architecture:** cache/security 服务 + RateLimitMiddleware 改造。

**Tech Stack:** Redis + FastAPI。

---

### Task 1: 缓存与安全服务

**Files:**
- Create: `backend/app/services/cache.py`、`backend/app/services/security_service.py`
- Modify: `backend/app/core/config.py`、`.env*`

### Task 2: 分布式限流

**Files:**
- Modify: `backend/app/core/rate_limit.py`、`backend/app/main.py`

### Task 3: chat 接入

**Files:**
- Modify: `backend/app/services/chat_service.py`

### Task 4: 测试、容器实测、文档、归档

**Files:**
- Create: `backend/tests/test_security.py`
- Create: `docs/learning/阶段11/01~03`
