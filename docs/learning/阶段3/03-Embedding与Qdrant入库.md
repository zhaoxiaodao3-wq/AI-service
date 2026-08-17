# 03 · Embedding 与 Qdrant 入库

## 做了什么

切片生成后调用 `model_adapter.embed_texts` 把文本转成向量，然后由 `vector_repo.upsert_document_chunks` 写入 Qdrant 的 `document_vectors` 集合。

每个 Qdrant 点包含：

```json
{
  "doc_id": 1,
  "user_id": 1,
  "text": "苹果是红色的",
  "chunk_index": 0
}
```

向量本身与 payload 一起存储，检索时直接算余弦相似度。

## 为什么

Embedding 的意义是把“语义相似”变成“向量距离近”。“苹果是红色的”和“苹果是什么颜色”虽然字面不同，但向量距离近，所以能被检索到；关键词搜索做不到这一点。

## 原理

### 两种 Embedding 模式

- `EMBEDDING_MODE=api`：调用 LiteLLM 的 `aembedding`，接入真实模型（如 `embedding-2`）。
- `EMBEDDING_MODE=local`：开发期兜底，用字符二元组哈希生成 1024 维向量，不依赖任何付费 API。

本地哈希向量只适合演示链路，不追求语义质量；生产必须切回真实 Embedding 模型。

本项目已切换真实 Embedding：`EMBEDDING_MODE=api` + 硅基流动 `BAAI/bge-m3`（1024 维），上传与知识库问答均实测通过。

### Qdrant 集合维度

集合在启动时按 `EMBEDDING_DIMENSIONS` 创建。向量维度必须和 Embedding 模型输出一致，否则上传/检索会报维度错误。维度不匹配时开发期直接删除重建集合。

### 向量 ID

用 `doc_id + chunk_index` 生成稳定的 UUID，保证同一文档重复上传时 ID 可预测，删除时按 `doc_id` 过滤即可。

## 命令解释

```powershell
docker exec aigc-backend python -c "import asyncio; from app.adapters.model_adapter import embed_texts; print(asyncio.run(embed_texts(['测试'])))"
```

在容器里直接验证向量化，返回一个 1024 维列表。

```powershell
Invoke-RestMethod -Uri http://localhost:6333/collections/document_vectors
```

查看集合状态：`points_count` 是当前向量数，`size` 是维度。

## 避坑

- 真实 Embedding API 需要余额/资源包；智谱 `embedding-2` 在无资源包时会返回 `余额不足或无可用资源包`。
- HuggingFace 本地模型下载在当前网络不可达，所以开发期用本地哈希向量兜底，不要强行依赖下载。
- Qdrant 点 ID 用 UUID 字符串；手写非 UUID 字符串会被拒绝。
- payload 里一定要带 `user_id`，否则阶段 4 多用户时检索会串数据。
