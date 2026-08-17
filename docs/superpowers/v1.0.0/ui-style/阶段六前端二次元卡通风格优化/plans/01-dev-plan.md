# 阶段六前端二次元卡通风格优化 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 用 ui-ux-pro-max 设计系统把前端改为二次元卡通风。

**Architecture:** CSS 变量 + scoped CSS，不改功能逻辑。

**Tech Stack:** Vue3 + Element Plus + CSS。

---

### Task 1: 全局 token 与样式

**Files:**
- Modify: `frontend/src/style.css`

**Step 1:** 字体、色板、背景、Element Plus 覆盖。

### Task 2: 顶栏与首页

**Files:**
- Modify: `frontend/src/layouts/MainLayout.vue`
- Modify: `frontend/src/views/HomeView.vue`

**Step 1:** 卡通顶栏与首页。

### Task 3: 聊天页

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 侧栏/消息/输入区/状态全部卡通化。

### Task 4: 上传页

**Files:**
- Modify: `frontend/src/views/UploadView.vue`

**Step 1:** 上传盒与文档卡片卡通化。

### Task 5: 验证与归档

**Step 1:** `pnpm build`。

**Step 2:** Edge 截图桌面/移动端。

**Step 3:** 学习文档 + archive + `pnpm harness:check`。
