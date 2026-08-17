# 阶段六前端聊天布局交互优化修订 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 撤销不合理的居中输入实现，改为标准底部输入 + 空态居中 + 回底按钮。

**Architecture:** 标准 flex 布局 + scroll 节流 + 无障碍属性。

**Tech Stack:** Vue3 + CSS。

---

### Task 1: 撤销居中输入

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 删除 centeredInput/center-hint/居中 transform。

### Task 2: 布局与滚动

**Files:**
- Modify: `frontend/src/layouts/MainLayout.vue`
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 整高 flex + 侧栏内部滚动。

**Step 2:** 回底按钮 rAF 节流与 reduced-motion。

### Task 3: 无障碍

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 文本域与图标按钮 aria-label。

### Task 4: 验证与归档

**Step 1:** `pnpm build`。

**Step 2:** Edge 截图桌面/移动端。

**Step 3:** archive + `pnpm harness:check`。
