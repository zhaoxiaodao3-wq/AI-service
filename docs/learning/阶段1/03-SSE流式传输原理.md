# 03 · SSE 流式传输原理

## 这一步做了什么

实现了后端 SSE 流式对话接口 `POST /api/chat/stream`：

- 请求体：`{ messages, model }`
- 响应：`text/event-stream`，逐段推送 `delta`，结束发 `done`，异常发 `error`
- 服务层 `chat_service`：截断上下文 → 调适配层 → 转 SSE 事件
- 3 个单元测试覆盖：正常流、参数校验、异常事件

## 为什么要这么做

AI 生成一段回答通常要几秒到几十秒。如果等它全部生成完再一次性返回：

- 用户盯着空白屏幕干等
- 体验差，像「卡死了」

SSE 让后端**生成一点、推送一点**，前端实时追加，形成「AI 打字」效果。这正是主流 AI 聊天产品的交互方式。

## 底层原理

### HTTP 只能一问一答吗

普通请求：浏览器发请求 → 服务器算完 → 一次性返回 → 连接关闭。

SSE：服务器保持连接不关闭，把数据**分多次**通过同一个连接推给浏览器，直到结束。浏览器可以边收边渲染。

### SSE 报文格式

每个事件两行：

```text
data: {"type":"delta","content":"你"}

```

- 每行以 `data: ` 开头，后面是 JSON
- 事件之间用一个空行分隔
- 浏览器/前端按空行切分即可解析

我们的事件协议：

| type | 含义 |
|------|------|
| `delta` | 模型输出增量，追加显示 |
| `done` | 流结束 |
| `error` | 出错，附 code/message |

### FastAPI 怎么实现

```python
return StreamingResponse(
    event_stream(),           # 异步生成器，yield 一段就推一段
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", ...},
)
```

`event_stream()` 是异步生成器，`yield` 的每一段都会被立即发送，连接保持到生成器结束。

### 为什么加那些响应头

- `Cache-Control: no-cache`：流式内容不能被浏览器/代理缓存
- `X-Accel-Buffering: no`：关掉 Nginx 类网关缓冲，否则它攒满才转发，打字效果失效
- `Connection: keep-alive`：保持长连接

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `pytest tests/test_chat_stream.py -v` | 验证 SSE 事件序列 |
| `curl -N -X POST http://localhost:8000/api/chat/stream ...` | 真实请求流式接口，`-N` 禁止缓冲逐字显示 |

## 常见问题与避坑

1. **`error` 变 `unknown`**：确认异常在适配层被映射成 `ModelError`，否则会被兜底吞掉。
2. **前端收不到流**：检查浏览器 Network 里 `content-type` 是否为 `text/event-stream`，以及是否有代理在缓冲。
3. **事件切分错乱**：SSE 按 `\n\n` 切分，跨块数据要留 buffer，不要每次只处理当前块。
4. **mock 生成器**：测试里 mock `stream_chat` 必须写成 async generator（函数体内有 `yield`），否则 `async for` 会失败。
