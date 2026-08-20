# 阶段九RAG增强Rerank混合检索引用溯源 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 3 的纯向量检索对专有名词/ID 不友好，且没有答案来源。本阶段加入关键词检索 + RRF 融合、Rerank 精排、引用溯源。

## 设计

### 1. 文档切片落 PG

- 新增 `DocumentChunk` 表：`document_id`、`chunk_index`、`content`。
- 上传文档时同步写 Qdrant 与 PG，删除文档时级联删除。
- 关键词检索用 PostgreSQL `ILIKE`。

### 2. 混合检索（`backend/app/services/retrieval_service.py`）

```text
向量检索 TopK（Qdrant）
+ 关键词检索 TopK（PG ILIKE）
→ 按 (doc_id, chunk_index) 合并
→ RRF 融合排序
→ 可选 Rerank 精排
```

- RRF 公式：`score = sum(1 / (k + rank))`，`k=60`。

### 3. Rerank

- `model_adapter.rerank(query, documents)` 调 SiliconFlow `/v1/rerank`。
- `BAAI/bge-reranker-v2-m3` 已实测可用。
- 失败时回退 RRF 排序，不阻塞聊天。

### 4. 引用溯源

- `done` 事件增加 `citations: [{doc_id, chunk_index, text, filename}]`。
- 前端 AI 消息下方展示引用 chip。

### 5. 配置

- `rerank_enabled=true`
- `rerank_model=BAAI/bge-reranker-v2-m3`
- `rerank_api_key/base_url` 缺省回退 Embedding/LLM 配置
- `vector_retrieve_k=8`、`keyword_retrieve_k=8`、`rrf_k=60`

## 验收标准

- [x] 上传文档后切片同时落 PG 与 Qdrant。
- [x] 混合检索返回 RRF 融合结果。
- [x] Rerank 可用时精排生效，失败回退。
- [x] `done` 事件包含 citations。
- [x] 前端展示引用。
- [x] `pytest -q`（31 passed）与 `pnpm build` 通过。
- [x] 学习文档 3 篇齐全。

## 非目标

- 不做 BM25 库（PG ILIKE 演示关键词检索）。
- 不做文档在线预览/引用跳转页面（阶段 13）。
