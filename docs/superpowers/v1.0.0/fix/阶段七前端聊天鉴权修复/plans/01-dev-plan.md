# 阶段七前端聊天鉴权修复 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 让 SSE 聊天请求携带 JWT。

**Architecture:** 在原生 fetch 请求中显式添加 Authorization 头。

**Tech Stack:** Vue3 + fetch。

---

### Task 1: 修复 chatStream

**Files:**
- Modify: `frontend/src/api/chatStream.ts`

**Step 1:** 添加 Token 头与 401 处理。

### Task 2: 验证

**Step 1:** `pnpm build`。

**Step 2:** 重建前端容器，Playwright 登录并发消息确认请求带 Token。
