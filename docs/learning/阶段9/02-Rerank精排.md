# 02 · Rerank 精排

## 做了什么

混合检索得到候选后，用 `BAAI/bge-reranker-v2-m3` 精排，再取 TopK 进 Prompt。

## 为什么

Embedding 检索是“粗排”，Rerank 模型会同时看“问题 + 文档”，判断是否真的相关，精度更高。

## 原理

```text
混合检索 TopK(8)
  → rerank(query, documents)
  → relevance_score 排序
  → 取 TopK(3)
```

SiliconFlow 接口：

```text
POST /v1/rerank
{"model":"BAAI/bge-reranker-v2-m3","query":"...","documents":[...]}
```

返回每个文档的 `relevance_score`。

## 命令解释

```powershell
$body = '{"model":"BAAI/bge-reranker-v2-m3","query":"苹果是什么颜色","documents":["苹果是红色的","香蕉是黄色的"]}'
Invoke-RestMethod -Uri https://api.siliconflow.cn/v1/rerank -Method Post -ContentType "application/json" -Body $body -Headers @{Authorization="Bearer $key"}
```

## 避坑

- Rerank 失败必须回退 RRF 排序，不能阻塞聊天。
- Rerank 是付费 API，生产要控制候选数量与调用频次。
- 候选数量太少 Rerank 没有意义，一般 8-20 条。
