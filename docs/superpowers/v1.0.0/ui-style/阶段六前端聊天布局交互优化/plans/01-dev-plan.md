# 阶段六前端聊天布局交互优化 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 侧栏整高滚动、输入框居中→落底动画、消息区独立滚动与回底按钮。

**Architecture:** ChatView 状态类 + CSS transform 过渡 + scroll 事件控制按钮。

**Tech Stack:** Vue3 + CSS。

---

### Task 1: 侧栏整高

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 保证 `.chat-page/.sidebar/.session-list` 高度与滚动链。

### Task 2: 居中输入与落底动画

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 增加 `centeredInput`、居中态 CSS transform。

### Task 3: 消息滚动与回底按钮

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** scroll 监听、按钮显隐、平滑回底。

### Task 4: 验证与归档

**Step 1:** `pnpm build`。

**Step 2:** Edge 截图桌面/移动端。

**Step 3:** archive + `pnpm harness:check`。
