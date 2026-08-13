# 阶段一：基础 AI 对话 + 多模型对接 + 短期记忆 · 开发规格

**Requirement:** [requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 1. 概述

在阶段 0 的骨架上打通核心对话链路：实现 LiteLLM 二次封装适配层（官方/中转双模式）、SSE 流式对话接口、短期上下文与 Token 截断、前端聊天页流式渲染，以及完整异常容错。

本阶段数据不持久化：会话消息由前端内存维护，阶段 2 再落库。

## 2. 设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 模型调用 | LiteLLM `acompletion`（异步） | 与 FastAPI 异步栈一致，不阻塞事件循环 |
| 流式接口 | FastAPI `StreamingResponse` + SSE | 标准、简单、可被 Vite 代理 |
| 前端流式 | fetch + `ReadableStream` 解析 SSE | `EventSource` 不支持 POST，本接口需要传消息体 |
| 上下文上限 | `MAX_CONTEXT_TOKENS=4000` 可配置 | 常见小模型窗口下限，保守不溢出 |
| Token 估算 | tiktoken 优先，字符估算兜底 | tiktoken 准确但需要模型匹配，兜底保证通用 |
| 模型清单 | 配置静态清单 + `GET /api/models` | 阶段 2 才入库，现在配置化 |
| 中转优先 | `LLM_PROXY_*` 非空则走中转 | 符合手册「中转仅用于开发调试」 |
| 会话状态 | 前端维护 messages，每次全量发送 | 阶段 2 前最小实现，便于理解 |

## 3. 架构与数据流

```text
前端聊天页（Vue3）
  │  POST /api/chat/stream { messages, model }
  ▼
backend api/chat.py（SSE 响应）
  │
  ▼
services/chat_service.py
  ├─ context_builder 拼接历史 + Token 截断
  │
  ▼
adapters/model_adapter.py（LiteLLM 二次封装）
  ├─ 官方模式：LLM_API_KEY / LLM_BASE_URL
  └─ 中转模式：LLM_PROXY_API_KEY / LLM_PROXY_BASE_URL
  ▼
LiteLLM → 厂商 API → 逐段文本增量 → SSE delta/done/error 事件
```

## 4. 接口契约

### 4.1 获取模型列表

`GET /api/models`

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "mode": "proxy",
    "models": ["gpt-4o", "gpt-4o-mini", "deepseek-chat", "claude-3-5-sonnet-20241022"],
    "default_model": "gpt-4o"
  }
}
```

- `mode`：`official`（官方直连）或 `proxy`（中转），由配置决定。
- 模型清单来自 `Settings.models` 常量，`default_model` 取 `LLM_MODEL`。

### 4.2 流式对话

`POST /api/chat/stream`

请求体：

```json
{
  "messages": [
    { "role": "user", "content": "你好" },
    { "role": "assistant", "content": "你好，有什么可以帮你？" }
  ],
  "model": "gpt-4o"
}
```

响应 `Content-Type: text/event-stream`，事件格式：

```text
data: {"type":"delta","content":"你"}

data: {"type":"delta","content":"好"}

data: {"type":"done","usage":{"prompt_tokens":12,"completion_tokens":8}}

data: {"type":"error","code":"invalid_key","message":"API Key 无效，请检查配置"}
```

约定：

- `delta`：模型输出增量，直接追加显示。
- `done`：流结束，携带 usage。
- `error`：任意异常时发出并结束流，`code` 供前端分类提示。
- 事件以 `\n\n` 分隔；每条 `data:` 为一行 JSON。
- 响应头：`Cache-Control: no-cache`、`X-Accel-Buffering: no`、`Connection: keep-alive`。

## 5. 模型适配层协议

`backend/app/adapters/model_adapter.py`：

```python
class ModelError(Exception):
    code: str      # invalid_key / insufficient_quota / timeout / stream_broken / unknown
    message: str   # 用户可读中文信息

@dataclass
class ChatRequest:
    model: str
    messages: list[dict]
    temperature: float = 0.7

@dataclass
class ChatResponse:
    content: str
    usage: dict | None

async def chat(request) -> ChatResponse      # litellm.acompletion
async def stream_chat(request) -> AsyncIterator[str]  # litellm.acompletion(stream=True)
```

异常映射：

| LiteLLM/底层异常特征 | ModelError.code |
|----------------------|-----------------|
| 401 / 认证失败 | `invalid_key` |
| 429 / quota 相关 | `insufficient_quota` |
| 超时（httpx.TimeoutException） | `timeout` |
| 流中断 / 解析失败 | `stream_broken` |
| 其余 | `unknown` |

未配置任何 Key 时直接抛 `invalid_key`，提示用户配置 `.env`。

## 6. 短期上下文与 Token 截断

`backend/app/services/context_builder.py`：

- `estimate_tokens(text, model)`：优先 tiktoken `encoding_for_model(model)`；异常时用估算函数 `中文字符数 + ceil(英文单词数 * 1.3)`。
- `truncate_messages(messages, max_tokens)`：
  - system 消息（若有）保留且不参与删除。
  - 从最早的非 system 消息开始删除，直到估算总 token ≤ 上限。
  - 全部删完仍超限时，只保留最近一条消息。
- 配置 `MAX_CONTEXT_TOKENS` 默认 4000。

## 7. 前端流式渲染

`frontend/src/api/chatStream.ts`：

- 使用 `fetch('/api/chat/stream', { method:'POST', headers, body })`。
- 读取 `response.body.getReader()`，按 `\n\n` 切分事件，解析 `data:` JSON。
- 回调：`onDelta(content)`、`onDone(usage)`、`onError(code, message)`。

`ChatView.vue` 状态：

- `messages: Array<{role, content}>`（内存态，阶段 2 落库）。
- 发送时：追加用户消息 → 追加空的 AI 消息 → 调 `chatStream` → delta 追加到 AI 消息。
- 模型下拉：挂载时 `GET /api/models`，选中值作为请求 `model`。
- 错误处理：`onError` 停止渲染，AI 消息内容替换为友好提示（或单独错误气泡）。

### 7.1 豆包风格页面布局

`MainLayout.vue` 改为左右结构：

```text
el-container（横向）
├── aside 左侧菜单（约 240px）
│   ├── 品牌区
│   ├── 「+ 新会话」按钮
│   └── 历史会话列表（会话标题）
└── container（右侧）
    ├── header 模型下拉 + 会话标题
    └── main 路由内容（聊天页/首页/上传页）
```

- 历史会话由 `ChatView` 内存维护：`sessions: [{ id, title, messages }]` + `activeSessionId`。
- 新会话：创建 `{ id: uuid, title: "新会话 N", messages: [] }` 并激活。
- 切换会话：`activeSessionId` 变更后聊天区显示对应 messages。
- 阶段 1 不持久化；阶段 2 改后端接口。

### 7.2 输入区与附件上传

聊天输入区：

- 左侧两个按钮：上传文件（📎）、上传图片（🖼），用 Element Plus 图标。
- 选中文件后显示附件条：文件名/图片缩略图 + 删除按钮。
- 消息结构：

  ```ts
  interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    attachments?: { name: string; type: string; url?: string }[]
  }
  ```

- 发送时 `attachments` 一并放进消息 dict；后端 `messages: list[dict]` 原样透传（阶段 1 不解析），模型只拿文本。
- 图片用 `URL.createObjectURL` 生成本地预览；附件仅存在于本次会话内存。

### 7.3 布局验收

- [ ] 左侧菜单含新会话按钮与历史会话列表。
- [ ] 新会话/历史会话切换正确。
- [ ] 右侧为聊天区，输入框支持文件与图片上传并展示附件。
- [ ] 附件随消息发送，后端阶段 1 忽略该字段不报错。

## 8. 错误处理

| 场景 | 行为 |
|------|------|
| 请求体校验失败 | 422 统一 JSON 错误 |
| 未配置 Key | SSE `error: invalid_key` |
| 模型调用异常 | 适配层映射 `ModelError` → SSE `error` |
| 前端 fetch 失败 | 错误提示 + 恢复输入框 |
| 流中断 | `error: stream_broken`，提示重新发送 |

## 9. 任务设计

### 9.1 适配层实现（T1）

- 实现 `model_adapter.py` 的 `chat` / `stream_chat` / `ModelError`。
- 增加 `_resolve_credentials()`：官方/中转选择。
- 测试：`tests/test_model_adapter.py`（用 mock 的 litellm，不真实调 API）。

### 9.2 模型配置与列表接口（T2）

- `config.py` 增加 `models`、`max_context_tokens`。
- `api/models.py` 实现 `GET /api/models`。
- 测试：`tests/test_models.py`。

### 9.3 SSE 对话接口（T3）

- `schemas/chat.py`：`ChatStreamRequest`（messages/model）。
- `api/chat.py`：`POST /api/chat/stream`，SSE 事件序列化。
- `services/chat_service.py`：组装（截断 → 适配层 → 事件）。
- 测试：`tests/test_chat_stream.py`（mock 适配层，验证事件序列）。

### 9.4 上下文截断（T4）

- `services/context_builder.py` 实现估算与截断。
- 测试：`tests/test_context_builder.py`（中文/英文/超长/系统消息保留）。

### 9.5 前端流式对接（T5）

- `src/api/chatStream.ts` SSE 解析器。
- `ChatView.vue` 真实交互 + 模型下拉。
- `MainLayout.vue` 不修改。

### 9.6 异常容错与联调（T6）

- 补齐错误分支 UI 与提示。
- 配置真实 Key 后全链路实测（有 Key 则验；无 Key 验错误分支）。

### 9.7 学习文档与注释（T7）

- `docs/learning/阶段1/01~06` 六篇。
- 全量代码注释规范自检。

## 10. 测试与验收

### 后端单测

- [ ] `pytest` 全绿：适配层 mock、模型列表、SSE 事件序列、上下文截断。
- [ ] SSE 事件格式符合契约（delta/done/error）。

### 真实联调

- [ ] `GET /api/models` 返回模型清单。
- [ ] 配置有效 Key 后，`POST /api/chat/stream` 逐段返回内容（中文正常）。
- [ ] 前端多轮对话 + 打字效果 + 模型切换正常。
- [ ] 错误分支（无 Key / 错误 Key）前端显示友好提示。

### 文档与注释

- [ ] 六篇学习文档齐全。
- [ ] 代码注释符合规范（方法/块/行注释）。

## 11. 不在本期范围

- 会话/消息持久化、用户体系、APIKey 加密入库（阶段 2）
- RAG 文档问答（阶段 3）
- 长期向量记忆（阶段 4）
- 调用统计、限流、完整日志系统（阶段 5）

## 12. 学习文档清单

```text
docs/learning/阶段1/
├── 01-LiteLLM与模型适配层原理.md
├── 02-官方Key与中转Key的区别.md
├── 03-SSE流式传输原理.md
├── 04-LLM上下文窗口与Token截断.md
├── 05-前端流式渲染与打字效果.md
└── 06-对话异常容错设计.md
```

每篇固定五小节：做了什么 / 为什么 / 原理 / 命令解释 / 避坑。
