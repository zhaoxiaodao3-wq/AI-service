# 04 · 相似度检索与 RAG Prompt

## 做了什么

聊天请求增加 `use_rag: true` 后，`chat_service` 会：

1. 取最后一条用户问题。
2. 把问题向量化。
3. 在 Qdrant 中按 `user_id` 过滤，取 TopK 且相似度超过阈值的片段。
4. 命中时把片段拼进系统提示词，再走原有流式对话。

`RAG_TOP_K=3`、`RAG_SCORE_THRESHOLD=0.35` 是默认调参值。

## 为什么

直接问模型“苹果是什么颜色”，模型会用常识回答；检索后，模型被要求“只依据资料回答”，回答就变成基于你的文档。相似度阈值用来过滤“看起来像但其实无关”的片段，避免误导模型。

## 原理

### 检索

```text
问题 → Embedding → Qdrant search
  query_filter: user_id = 1
  limit: top_k
  score_threshold: 0.35
```

余弦相似度越接近 1 表示越相关。阈值太高会漏召回，太低会引入噪声，需要按知识库内容调。

### Prompt 组装

```text
[系统] 你是一名知识库问答助手。请只依据以下资料回答：
[片段1] 苹果是红色的
[片段2] ...

[用户] 苹果是什么颜色？
```

系统提示词中明确“只依据资料回答，资料不足时如实说明”，能显著减少模型幻觉。

## 命令解释

```powershell
$body = '{"messages":[{"role":"user","content":"苹果是什么颜色？"}],"model":"glm-4-flash","use_rag":true}'
Invoke-RestMethod -Uri http://localhost:8000/api/chat/stream -Method Post -ContentType "application/json" -Body $body
```

开启知识库问答的流式请求。

## 避坑

- 检索前必须上传过文档，否则 Qdrant 里没有向量，回答会退化成普通聊天。
- 本地哈希向量质量有限，检索命中可能不如真实 Embedding 精准，这是预期内的开发模式。
- 阈值建议先看真实 score 再调：本地跑一次检索，把 score 打印出来，而不是拍脑袋设 0.35。
- 命中片段要按相关度排序，避免把低相关片段排前面影响回答。
