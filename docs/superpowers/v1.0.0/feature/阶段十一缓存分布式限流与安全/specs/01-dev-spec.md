# 阶段十一缓存分布式限流与安全 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### 1. 模型响应缓存

- `services/cache.py`：Redis get/set，TTL 可配置。
- `chat_service`：普通聊天按 `chat:{model}:{sha256(question)}` 缓存，RAG/工具不缓存。

### 2. 分布式限流

- `core/rate_limit.py` 改用 Redis ZSET 滑动窗口。
- 支持 IP 与登录用户两种 key；Redis 异常回退内存。

### 3. Prompt 注入

- `services/security_service.py` 正则检测常见注入模式。
- 命中返回 SSE `prompt_injection` 错误并记录日志。

### 4. SSRF

- `validate_url`：scheme 校验 + DNS 解析后检查所有 IP。

## 验收标准

- [x] 模型响应缓存命中返回缓存。
- [x] Redis 分布式限流按 IP/用户生效。
- [x] Prompt 注入被拦截并返回错误事件。
- [x] SSRF 校验拦截内网地址。
- [x] `pytest -q`（34 passed）与 `pnpm build` 通过。
- [x] 学习文档 3 篇齐全。
