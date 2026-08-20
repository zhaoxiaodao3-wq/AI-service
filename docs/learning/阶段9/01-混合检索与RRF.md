# 01 · 混合检索与 RRF

## 做了什么

RAG 检索从“纯向量”升级为“向量 + 关键词”混合：

- 向量检索：Qdrant 按相似度召回。
- 关键词检索：PostgreSQL `ILIKE` 在切片原文中匹配。
- RRF（Reciprocal Rank Fusion）融合两个榜单。

## 为什么

纯向量检索对专有名词、ID、精确写法不敏感；关键词检索则擅长精确匹配。混合后两类结果互相补充。

## 原理

### 切片落 PG

新增 `document_chunks` 表，上传时把切片原文写入 PostgreSQL，向量仍存 Qdrant。

### RRF 公式

```text
score = sum(1 / (k + rank))
k = 60
```

同一个片段在向量榜排第 2、关键词榜排第 5：

```text
score = 1/(60+2) + 1/(60+5) ≈ 0.0161 + 0.0154
```

只在一个榜单出现的片段分数天然偏低，实现“两榜都高才稳”。

## 命令解释

```powershell
docker exec aigc-postgres psql -U aigc_user -d aigc_chat -c "SELECT COUNT(*) FROM document_chunks;"
```

查看切片落库数量。

## 避坑

- 切片必须按 `(document_id, chunk_index)` 去重，否则 RRF 会重复计分。
- 关键词检索用 `ILIKE` 只是演示，生产可换 PostgreSQL FTS/trigram 或 BM25。
- 向量召回阈值在混合前建议放开到 0，避免把关键词命中直接丢掉。
