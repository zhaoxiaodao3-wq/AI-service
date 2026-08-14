# 阶段一前端打字机流式效果 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 内容一到达就展示，并用打字机动画逐段输出。

**Architecture:** SSE 回调进入待展示缓冲区，定时器按节奏追加到响应式消息内容；加载动画只保留到第一个 delta 前。

**Tech Stack:** Vue 3 + TypeScript。

---

### Task 1: 打字机状态与缓冲区

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 新增 `hasStreamedContent`、`pendingText`、`revealTimer`、`flushTypewriter()`、`startReveal()`。

**Step 2:** `onDelta` 改为写入缓冲区并启动定时器；`onDone`/`onError`/catch 调用 `flushTypewriter()`；卸载时清理定时器。

### Task 2: 模板状态切换

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 加载动画行改为 `v-if="loading && !hasStreamedContent"`。

**Step 2:** AI 内容输出中追加闪烁光标，流结束后消失。

### Task 3: 构建验证与归档

**Step 1:** 运行 `pnpm build`，期望通过。

**Step 2:** 写 archive，勾选 spec 验收项，跑 `pnpm harness:check`。
