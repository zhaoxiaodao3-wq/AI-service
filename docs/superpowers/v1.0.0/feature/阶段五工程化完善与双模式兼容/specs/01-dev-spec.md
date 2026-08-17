# 阶段五工程化完善与双模式兼容 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 2 已把模型配置存进 `ai_models`（API Key 加密），但聊天仍走 `.env` 全局配置。本阶段让聊天按所选模型读取数据库配置，增加流式重试、聊天限流，并用 `model_calls` 表统计每次调用。

## 设计

### 1. 配置

`backend/app/core/config.py` 新增：

- `llm_retry_count=1`
- `rate_limit_per_minute=30`

`.env.example` 同步。

### 2. 按模型读取配置

`model_adapter._resolve_credentials(model_name=None)`：

1. 优先查 `ai_models`：有该模型且 `api_key_encrypted` 非空时，解密后使用 `base_url`。
2. 无配置时回退 `.env` 的中转/官方配置。

`chat()` 与 `stream_chat()` 调用时传入模型名。

### 3. 流式重试

`stream_chat` 增加重试：`llm_retry_count + 1` 次尝试；已产生过 `delta` 后不再重试，避免重复内容。

### 4. 限流

新增 `backend/app/core/rate_limit.py` 的 ASGI 中间件，仅限制 `POST /api/chat/stream`：

- 按客户端 IP 滑动窗口计数。
- 超过 `rate_limit_per_minute` 返回 HTTP 429。
- 不影响其他接口。

### 5. 调用统计

新增 `ModelCall` 表：

- `id`、`session_id`（可空）、`model`、`success`、`token_count`、`duration_ms`、`created_at`

聊天流结束时写入一条记录；Token 数为估算值。

`GET /api/stats` 返回：

- 总调用次数
- 成功率
- 总 Token
- 按模型分组统计

### 6. 文档

新增 `docs/learning/阶段5/01~04`：

1. 双模式兼容与按模型配置
2. 限流与流式重试
3. 模型调用统计
4. 工程化验收与运维建议

## 验收标准

- [x] 聊天按 `ai_models` 配置调用模型，无配置回退 `.env`。
- [x] 流式失败在未输出内容时自动重试。
- [x] chat 接口限流返回 429。
- [x] `GET /api/stats` 返回调用次数/成功率/Token/按模型统计。
- [x] `pytest -q`（24 passed）与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 非目标

- 不做前端统计看板（Adminer/API 可查看）。
- 不做分布式限流与多实例协调（单机开发足够）。
