# 01 · LiteLLM 与模型适配层原理

## 这一步做了什么

实现了 `backend/app/adapters/model_adapter.py`，这是项目所有 AI 调用的唯一入口：

- `chat()`：非流式对话，一次返回完整回答
- `stream_chat()`：流式对话，逐段返回文本增量
- `ModelError`：统一异常类型，把各种底层错误翻译成友好提示
- `_resolve_credentials()`：自动在「官方直连 / 中转」之间切换

并用 mock 写了 3 个单元测试（不真实调模型、不花一分钱）。

## 为什么要这么做

项目要对接多个厂商（OpenAI、DeepSeek、Claude、智谱），每个厂商的 SDK 风格不同：

- 有的返回 `data.choices[0].message.content`
- 有的是同步、有的是异步
- 出错信息五花八门

如果每个地方都直接写 SDK 调用，代码会到处都是「厂商差异」。适配层的意义：

1. **统一入口**：业务代码只认识 `chat()` / `stream_chat()`，不关心底层是谁。
2. **统一格式**：入参 `ChatRequest`、出参 `ChatResponse` 全项目一致。
3. **统一错误**：任何厂商报错都转成 `ModelError`，前端按 `code` 提示。
4. **可替换**：换模型/换厂商只改配置，不重写业务。

## 底层原理

### LiteLLM 是什么

LiteLLM 是一个「模型网关库」：给 100+ 厂商提供同一套 OpenAI 风格 API。我们传 `model` + `messages` + `api_key` + `api_base`，它负责翻译成各家协议。

它没有完全替代我们的适配层——手册要求「二次封装，不裸用」，因为 LiteLLM 的出参仍带厂商差异，且业务上还需要统一错误码。

### 官方直连 vs 中转切换

```python
def _resolve_credentials():
    if s.llm_proxy_api_key and s.llm_proxy_base_url:
        return s.llm_proxy_api_key, s.llm_proxy_base_url  # 中转优先
    if s.llm_api_key:
        return s.llm_api_key, s.llm_base_url or None        # 官方直连
    return None
```

原理：`.env` 里中转配置非空就优先走中转；否则走官方。以后你把智谱换掉，只需改 `.env`。

### 异步与流式

- `litellm.acompletion(...)`：异步请求，`await` 一次拿完整结果。
- `litellm.acompletion(..., stream=True)`：返回**异步生成器**，用 `async for` 逐块拿增量，不需要 `await`。

这就是「AI 打字效果」的后端来源：模型分块返回，我们分块转发。

### 统一异常映射

```python
if "auth" in text or "401" in text:
    return ModelError("invalid_key", "API Key 无效")
```

底层错误五花八门，我们按特征文本分类成 5 种 `code`：

| code | 含义 |
|------|------|
| `invalid_key` | Key 无效或未配置 |
| `insufficient_quota` | 额度不足 |
| `timeout` | 请求超时 |
| `stream_broken` | 流中断 |
| `unknown` | 其他未知错误 |

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `pytest tests/test_model_adapter.py -v` | 运行适配层单元测试 |
| `pytest -q` | 运行全部后端测试 |

测试用 `monkeypatch` 把 `litellm.acompletion` 替换成假函数，因此测试秒过、零成本。

## 常见问题与避坑

1. **`async_generator object can't be awaited`**：`stream=True` 时 `acompletion` 返回生成器，不要加 `await`。
2. **测试很慢**：首次导入 litellm 较慢属正常；之后有缓存会快。
3. **Key 无效**：确认 `backend/.env` 的 `LLM_API_KEY` 与 `LLM_BASE_URL` 配套（智谱要用 `/api/paas/v4`）。
4. **切换模型后没生效**：改的是 `.env` 要重启后端；模型下拉切换走请求参数，不影响配置。
