# 阶段四AI长期向量记忆 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 3 已有知识库 RAG，但 AI 仍不记得“上个会话聊过什么”。本阶段在每轮对话结束后生成记忆向量，跨会话提问时自动召回，并把长期记忆与短期上下文、知识库片段一起注入 Prompt。

## 设计

### 1. 配置

`backend/app/core/config.py` 新增：

- `memory_enabled=True`
- `memory_top_k=3`
- `memory_score_threshold=0.35`

`.env.example` 同步。

### 2. 向量仓库

`backend/app/repositories/vector_repo.py` 新增：

- `upsert_memory(user_id, session_id, text, vector)`：写入 `memory_vectors`，payload 含 `user_id/session_id/text/type=memory`。
- `search_memories(user_id, vector, top_k, threshold, exclude_session_id=None)`：按用户过滤，可选排除当前会话，返回相似记忆。
- `delete_session_memories(session_id)`：删除会话记忆（删除会话时联动）。

### 3. 记忆写入（`backend/app/api/chat.py`）

带 `session_id` 且对话有用户文本和 AI 文本时，流结束后生成记忆文本：

```text
用户：<最后一条用户消息>
AI：<完整回答或错误文案>
```

向量化后写入 `memory_vectors`。记忆写入失败只记 warning，不影响聊天结果。

### 4. 记忆召回（`backend/app/services/chat_service.py`）

- `stream_chat_events` 增加 `session_id` 参数。
- 有新用户问题时：Embedding 问题 → `search_memories(..., exclude_session_id=session_id)`。
- 命中记忆后调用 `build_rag_messages(messages, hits, memories)` 融合。
- 开启 `use_rag` 时同时注入知识库片段；记忆与知识库并存。

### 5. Prompt 组装

`document_service.build_rag_messages` 增加 `memories` 参数：

```text
[系统] 你是 AI 助手。请结合以下历史记忆与知识库资料回答：
历史记忆（跨会话）：
...
知识库资料：
...
[用户] 新问题
```

## 验收标准

- [x] 每轮对话结束自动写入一条记忆向量。
- [x] 新会话提问可召回上一会话的记忆并影响回答。
- [x] 当前会话记忆不重复注入（排除 session_id）。
- [x] 低于阈值的无关记忆不注入。
- [x] 与知识库问答可同时生效。
- [x] `pytest -q`（22 passed）与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 非目标

- 不做记忆编辑/删除界面（可复用文档删除思路后续扩展）。
- 不做用户级记忆隔离 UI（默认本地用户）。
