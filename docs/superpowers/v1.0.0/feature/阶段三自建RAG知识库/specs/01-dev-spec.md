# 阶段三自建RAG知识库 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 2 已把会话/消息/模型配置持久化。本阶段实现“文档上传 → 解析 → 切片 → 向量化 → 入库 → 检索 → 生成”的完整 RAG 链路，检索与入库逻辑全部手写，Embedding 模型通过 LiteLLM 统一调用。

## 设计

### 1. 配置（`backend/app/core/config.py` + `.env.example`）

- `embedding_mode`：`api`（LiteLLM 真实模型）或 `local`（开发期本地哈希向量兜底）
- `embedding_model`：默认 `embedding-2`
- `embedding_api_key` / `embedding_base_url`：为空时回退 LLM 配置
- `embedding_dimensions`：默认 `1024`，与 Qdrant 集合向量维度一致
- `chunk_size=500`、`chunk_overlap=50`
- `rag_top_k=3`、`rag_score_threshold=0.35`

### 2. Qdrant 集合

`backend/app/db/qdrant.py` 改为按 `embedding_dimensions` 建集合；已有集合维度不匹配时删除重建（开发期幂等）。

### 3. 文档实体与元信息

新增 `Document` 表：`id`、`user_id`、`filename`、`file_type`、`file_size`、`chunk_count`、`created_at`。切片原文只存 Qdrant payload，不重复落 PG。

### 4. 服务层

- `backend/app/services/chunker.py`：`split_text(text, chunk_size, overlap)`，按步长切片并保留重叠。
- `backend/app/services/document_service.py`：
  - `parse_file(content, filename)`：txt/md 直接解码，pdf 用 `pypdf` 提取文本。
  - `build_rag_messages(messages, hits)`：系统提示词 + 检索片段 + 原消息。
- `backend/app/repositories/vector_repo.py`：
  - `upsert_document_chunks(doc_id, user_id, chunks, vectors)`
  - `search_documents(user_id, vector, top_k, threshold)`
  - `delete_document_vectors(doc_id)`

### 5. Embedding 适配

`backend/app/adapters/model_adapter.py` 新增 `embed_texts(texts)`：

- `embedding_mode=api`：通过 `litellm.aembedding` 调用，统一异常映射。
- `embedding_mode=local`：使用字符二元组哈希向量（维度 1024），供无 Embedding 额度时开发验证。

### 6. 接口

`backend/app/api/documents.py`：

- `POST /api/documents`：multipart 上传，校验扩展名与大小（5MB），解析→切片→向量化→PG 元信息→Qdrant 入库。
- `GET /api/documents`：列出默认用户文档。
- `DELETE /api/documents/{id}`：删除 PG 元信息与 Qdrant 向量。

`ChatStreamRequest` 增加 `use_rag: bool = False`；`chat_service.stream_chat_events` 在开启时对最后一条用户问题做检索，命中片段则注入 RAG 系统提示词后正常流式回答。

### 7. 前端

- `UploadView.vue`：点击/拖拽选择 PDF/TXT/MD，上传后展示文档列表与删除按钮。
- `ChatView.vue`：输入区增加“知识库问答”开关，开启时请求带 `use_rag: true`。

### 8. 学习文档

`docs/learning/阶段3/01~05`，每篇五小节：

1. RAG 总览与文档解析
2. 文本切片原理与实现
3. Embedding 与 Qdrant 入库
4. 相似度检索与 RAG Prompt
5. 前端上传与知识库问答联调

### 9. 测试

- chunker 切片长度与重叠
- RAG prompt 组装
- 文档上传接口（mock embedding 与 Qdrant）
- 原有测试全部保持通过

## 验收标准

- [x] 上传 TXT/MD/PDF 成功，PG 有元信息，Qdrant 有切片向量。
- [x] 切片满足 chunk_size/overlap 约束。
- [x] 检索能按 TopK + 阈值返回相关片段。
- [x] 开启知识库问答后，回答内容基于上传文档。
- [x] 前端可上传、查看、删除文档，聊天可开关知识库。
- [x] `pytest -q`（21 passed）与 `pnpm build` 通过。
- [x] 学习文档 5 篇齐全且五小节完整。

## 非目标

- 不做文档在线预览与多格式 OCR。
- 不做记忆向量（阶段 4）。
- 不做文件存储后端（本地上传内存/磁盘临时处理，元信息落 PG）。
