# 阶段八Agent工具调用 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

当前系统只能“聊天 + RAG”，本阶段加入 Function Calling，让模型可以调用工具获取实时信息后再回答，升级为 Agent。

## 设计

### 1. 工具层

- `backend/app/tools/base.py`：Tool 定义（name/description/parameters/handler）。
- `backend/app/tools/registry.py`：工具注册与查询。
- `backend/app/tools/builtin.py`：
  - `get_current_time`：当前时间。
  - `calculator`：安全表达式计算（AST，不使用 eval）。
  - `search_knowledge`：当前用户知识库检索。
  - `list_documents`：当前用户文档列表。

### 2. 适配层

- `ChatRequest` 增加 `tools`。
- `ChatResponse` 增加 `tool_calls`。
- `chat()` 透传 tools 并解析 `message.tool_calls`。

### 3. Agent 循环（`chat_service`）

`stream_chat_events` 增加 `use_tools`：

```text
1. 模型带 tools 调用
2. 有 tool_calls → 逐个执行 → 追加 tool 消息 → 回到 1（最多 3 轮）
3. 无 tool_calls → 直接输出最终回答
```

每轮执行前发出 `tool_start`，执行后发出 `tool_done`；失败回退普通流式聊天。

### 4. 接口与前端

- `ChatStreamRequest` 增加 `use_tools`。
- `chatStream.ts` 支持 `useTools`。
- `ChatView` 增加“工具”开关，并展示工具调用提示。

## 验收标准

- [x] 工具注册中心可列出 OpenAI 格式 tools。
- [x] 计算器安全计算，不执行任意代码。
- [x] 聊天开启工具后能调用时间/计算器并基于结果回答。
- [x] SSE 输出 tool_start/tool_done。
- [x] 工具失败不阻塞聊天。
- [x] `pytest -q`（30 passed）与 `pnpm build` 通过。
- [x] 学习文档 3 篇齐全。

## 非目标

- 不做网页搜索/浏览器工具（可后续扩展）。
- 不做多 Agent 编排（后续阶段）。
