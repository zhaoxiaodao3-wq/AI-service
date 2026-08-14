# 阶段一前端打字机流式效果 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

当前 `ChatView.vue` 在流式期间始终显示“三点加载”行，并且 `delta` 直接追加到消息内容，速度快时看起来像一次性输出。本模块把“等待中”和“展示中”两个状态分开：第一个 `delta` 一到就进入展示态，并用缓冲区按打字机节奏逐段渲染。

## 设计

### 1. 状态拆分

- 新增 `hasStreamedContent` ref：发送时置 `false`，第一个 `delta` 到达时置 `true`。
- 加载动画行只在 `loading && !hasStreamedContent` 时显示；一旦有内容立即消失。
- `loading` 仍贯穿整个流，用于禁用发送按钮，防止流中重复发送。

### 2. 打字机缓冲区

在 `ChatView.vue` script 内维护：

```ts
let pendingText = ''
let revealTimer: number | undefined
```

- `onDelta` 把分片追加到 `pendingText`，并启动/保持 `setInterval`。
- 每个 tick 从 `pendingText` 取一小段追加到 `aiMsg.content`，实现打字机节奏。
- `onDone` / `onError` / catch / 组件卸载时调用 `flushTypewriter()`：清定时器并立即补全剩余内容。

### 3. 光标

AI 内容正在输出时，在消息末尾显示闪烁光标 `▍`，流结束后消失。

## 验收标准

- [x] 第一个 `delta` 到达后加载动画消失，内容直接展示。
- [x] 内容按打字机节奏逐段显示，不是一次性全部出现。
- [x] 流结束/错误时立即补全剩余内容，最终内容完整。
- [x] `pnpm build` 通过。
- [x] SSE 协议、后端日志、Docker 观测栈行为不变。

## 非目标

- 不改后端与 SSE 事件结构。
- 不做可配置打字速度（后续可加设置项）。
