# 04 · LLM 上下文窗口与 Token 截断

## 这一步做了什么

实现了 `backend/app/services/context_builder.py`：

- `estimate_tokens(text)`：估算一段文本的 token 数（tiktoken 优先，字符估算兜底）
- `truncate_messages(messages, max_tokens)`：超长时从最早消息开始删，system 提示词永远保留
- 3 个单元测试覆盖：中文估算、system 保留、短对话不变

## 为什么要这么做

大模型不是无限记忆的。每个模型有「上下文窗口」限制，例如 4K / 8K / 128K tokens。窗口包含：

```text
系统提示词 + 历史对话 + 你的新问题 ≤ 窗口上限
```

聊天聊久了，历史越来越长，迟早超限。超限的后果：

- 模型直接报错
- 或被静默截断，丢失关键上下文

短期记忆（本项目练手点）就是**手动管理历史**：装不下就把最旧的消息删掉，保住最近的对话。这比无脑全部发送更专业。

## 底层原理

### Token 是什么

Token 是模型处理文本的最小单位。英文里一个词常拆成 1~2 个 token；中文通常 1 个汉字约 1 个 token。模型按 token 计费、按 token 计上下文。

### tiktoken 怎么估算

```python
enc = tiktoken.encoding_for_model(model)
len(enc.encode(text))
```

tiktoken 是 OpenAI 的官方分词器，能按模型词表精确算出 token 数。它对 OpenAI 系模型最准；对其他厂商（智谱等）用通用词表也能给出合理近似。

### 兜底估算

```python
cn = 中文字符数
en = 英文字母数 // 4
token ≈ cn + en
```

为什么保守偏大？宁可多删一点历史，也不要让请求超限报错。

### 截断策略

```python
system = 系统提示词（永远保留）
others = 其余消息
while 总 token > 上限:
    others.pop(0)   # 删最早
```

类比：教室座位有限，先来的学生站起来让位，后来的学生坐。最新的对话永远保留，最旧的历史先被淘汰。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `pytest tests/test_context_builder.py -v` | 运行上下文截断测试 |

## 常见问题与避坑

1. **首次测试慢**：tiktoken 首次要下载词表文件，之后有缓存。
2. **估算不准**：跨厂商模型做不到 100% 精确，兜底公式已故意偏大。
3. **system 丢了**：截断逻辑里 system 单独保留，不要把它混进 others。
4. **上限设多大**：默认 4000，配小模型/长对话时可在 `.env` 调 `MAX_CONTEXT_TOKENS`（阶段 1 用 config 常量）。
