# 阶段六前端聊天布局交互优化修订 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 审查结论（ui-ux-pro-max）

- 固定元素必须考虑安全区与重叠，输入区采用标准底部布局。
- 空态应给出清晰提示与下一步动作，位置在内容区而非输入区。
- 高频 scroll 事件需要节流/防抖。
- 动效必须尊重 `prefers-reduced-motion`。
- 表单输入需要可访问标签。

## 设计

### 1. 输入区固定底部

- 删除 `centeredInput` 计算属性、`.center-hint`、居中 transform 与动画。
- `.input-area` 始终位于聊天区底部，`flex: none`。
- 空会话时“今天想聊点什么？”由消息区 `.empty-state` 居中展示。

### 2. 侧栏整高滚动

- `MainLayout`：`.layout` 高度 100vh，`.content { flex:1; min-height:0; overflow:hidden; }`。
- `ChatView`：`.chat-page { height:100%; min-height:0; overflow:hidden; }`。
- `.sidebar { height:100%; min-height:0; overflow:hidden; }`，`.session-list { overflow-y:auto; }`。

### 3. 回底按钮

- 消息区滚动时，距底部 > 160px 即显示按钮（不限消息条数）。
- 点击平滑滚动到底，滚到底自动隐藏。
- 使用 `requestAnimationFrame` 节流 scroll 回调。
- 按钮 `aria-label="回到底部"`，右下角悬浮在输入区上方，不遮挡消息。
- `prefers-reduced-motion` 时使用即时滚动。

### 4. 无障碍

- 文本域增加 `aria-label="聊天输入框"`。
- 图标按钮补充 `aria-label`。

## 验收标准

- [x] 输入框始终在底部；空会话提示居中在消息区。
- [x] 侧栏整高且内部滚动。
- [x] 回底按钮仅在不靠底时出现，点击平滑回底并隐藏。
- [x] `prefers-reduced-motion` 下无强制动画。
- [x] `pnpm build` 通过，桌面/移动端截图无溢出。

## 非目标

- 不引入第三方滚动库。
- 不改后端。
