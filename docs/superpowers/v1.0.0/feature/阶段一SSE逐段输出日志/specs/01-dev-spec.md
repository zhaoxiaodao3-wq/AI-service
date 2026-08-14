# 阶段一SSE逐段输出日志 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

当前 `backend/app/api/chat.py` 只在流结束时输出 `chat_stream finish` 汇总，Grafana 中看不到分片过程。本模块在每个 `delta` 事件到达时输出一行 INFO 日志，流结束后保留原汇总，实现“实时逐段 + 末尾汇总”。

## 设计

### 1. 逐段 delta 日志

在 `event_stream()` 内，`kind == "delta"` 时新增：

```text
chat_stream delta chunk='<本片内容前80字>' chunk_chars=N total_chars=N
```

- 内容压平换行并截断到 80 字，避免刷屏。
- `total_chars` 是当前累计字符数，方便观察进度。
- 级别 INFO，与现有日志格式一致。

### 2. 完整汇总

保留现有 `chat_stream finish`：`events={delta, done, error}`、`chars`、`preview`。

### 3. 测试

`backend/tests/test_access_log.py` 的 chat 用例增加断言：mock 两个分片时，日志中必须出现两条 `chat_stream delta`，且 `total_chars` 递增。

## 验收标准

- [x] 每个 delta 到达时输出 `chat_stream delta` 日志，含分片内容、分片字符数、累计字符数。
- [x] 流结束仍输出 `chat_stream finish` 完整汇总。
- [x] `pytest -q` 通过，新增 delta 日志断言生效。
- [x] Docker 后端重建后，Loki 查询能看到逐段 delta 日志。
- [x] SSE 接口协议与前端流式渲染行为不变。

## 非目标

- 不改前端。
- 不改 SSE 事件结构。
- 不做按时间/批次聚合（后续需要可扩展）。
