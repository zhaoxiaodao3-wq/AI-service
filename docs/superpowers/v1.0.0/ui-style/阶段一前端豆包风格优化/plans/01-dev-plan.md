# 阶段一前端豆包风格优化 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 在不改功能的前提下，将前端整体重构为豆包网页版式的浅色现代界面。

**Architecture:** 纯 Vue scoped CSS + 全局 CSS 变量覆盖 Element Plus 默认观感；聊天页保持现有数据流与组件结构，只重做布局与样式。

**Tech Stack:** Vue 3 + TypeScript + Element Plus + Vite。

---

### Task 1: 全局样式与顶部导航

**Files:**
- Modify: `frontend/src/style.css`
- Modify: `frontend/src/layouts/MainLayout.vue`

**Step 1:** 重写 `style.css`：页面背景 `#F5F6F7`、字体栈、滚动条、Element Plus 按钮/输入框全局微调。

**Step 2:** 重写 `MainLayout.vue`：56px 白色顶栏，左侧品牌区（渐变方块 logo + 名称），右侧导航菜单；内容区 `padding: 0`，让各页面自行控制留白。

**Step 3:** 验证：
```powershell
cd frontend; pnpm build
```
期望：`vue-tsc -b && vite build` 通过。

### Task 2: 聊天页结构重构

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 保留全部 `script setup` 逻辑（会话、模型、附件、流式发送）不动。

**Step 2:** 重写 template 为：左侧栏（品牌区/新对话按钮/会话列表）+ 主区（header/消息流/空态/输入区）。

**Step 3:** 消息流区分 user/assistant：用户气泡右对齐浅蓝，AI 左侧头像 + 白底正文；附件缩略图与文件 chip；加载中三点动画；错误提示条。

**Step 4:** 输入区改为底部居中白底圆角容器：附件/图片圆形图标按钮（带 tooltip）、自适应文本域、圆形发送按钮。

### Task 3: 聊天页样式与响应式

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

**Step 1:** 补齐 scoped CSS：侧栏 240px、消息区 max-width 760px、圆角/间距/阴影 token、hover/active 状态。

**Step 2:** `<=768px` 媒体查询：侧栏收窄为 64px，隐藏文字，会话项显示首字圆标。

**Step 3:** 验证构建：
```powershell
cd frontend; pnpm build
```
期望：通过。

### Task 4: 首页与上传页

**Files:**
- Modify: `frontend/src/views/HomeView.vue`
- Modify: `frontend/src/views/UploadView.vue`

**Step 1:** 首页改为居中品牌首屏：logo、标题、副标题、两个入口按钮。

**Step 2:** 上传页改为居中虚线占位：上传图标 + “文档上传将在阶段 3 接入”。

**Step 3:** 验证构建：
```powershell
cd frontend; pnpm build
```
期望：通过。

### Task 5: 视觉与回归验证

**Files:**
- 验证产物：`frontend/dist/`

**Step 1:** 启动 Vite preview/dev server，用 Playwright 截图桌面（1440x900）与移动端（390x844）检查：无重叠、无溢出、侧栏收窄生效。

**Step 2:** 手工走查功能：模型下拉、发送、流式渲染、会话切换、附件展示、错误提示。

**Step 3:** 记录截图路径，验收后进入归档。
