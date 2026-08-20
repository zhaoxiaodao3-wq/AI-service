# 阶段九RAG增强Rerank混合检索引用溯源 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-18
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

RAG 从纯向量升级为“向量 + 关键词 + RRF + Rerank”混合检索，并新增引用溯源：SSE `done` 携带 citations，前端展示文档名与 chunk 序号。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/models/entities.py`（DocumentChunk 表） |
| 改 | `backend/app/repositories/document_repo.py`（add_chunks/get_filenames） |
| 新增 | `backend/app/repositories/document_chunk_repo.py` |
| 新增 | `backend/app/services/retrieval_service.py`（RRF/Rerank） |
| 改 | `backend/app/adapters/model_adapter.py`（rerank） |
| 改 | `backend/app/api/documents.py`（切片落 PG） |
| 改 | `backend/app/services/chat_service.py`（hybrid + citations） |
| 改 | `backend/app/core/config.py`、`.env*` |
| 改 | `frontend/src/api/chatStream.ts`、`frontend/src/views/ChatView.vue`（引用展示） |
| 新增 | `backend/tests/test_retrieval.py` |
| 新增 | `docs/learning/阶段9/01~03` 共 3 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段九RAG增强Rerank混合检索引用溯源/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 上传文档后切片同时落 PG 与 Qdrant。
- [x] 混合检索返回 RRF 融合结果。
- [x] Rerank 可用时精排生效，失败回退。
- [x] `done` 事件包含 citations。
- [x] 前端展示引用。
- [x] `pytest -q`（31 passed）与 `pnpm build` 通过。
- [x] 学习文档 3 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无文档时关键词检索为空；有文档时返回候选与引用 |
| 常量/mock/真数据 | 通过 | RRF/关键词为真实代码；Rerank 失败回退 RRF |
| 多入口 | 通过 | 知识库开关、工具开关共用同一 chat 链路 |
| 失败/缺省 | 通过 | Rerank 余额不足时回退 RRF，不阻塞聊天 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- 后端测试：`pytest -q` → 31 passed。
- 前端构建：`pnpm build` 通过。
- Docker 实测：上传 TXT 200；RAG 问答 200，`done` 返回 citations（doc_id=9、chunk_index=0、filename=知识库.txt）。
- Rerank 接口实测：`BAAI/bge-reranker-v2-m3` 返回相关度分数。

## 遗留风险

- SiliconFlow 当前余额不足，Embedding 已切回 `EMBEDDING_MODE=local` 开发兜底；余额恢复后切回 api 可获得更高质量向量。
- Rerank 依赖同一 Key，余额不足时会自动回退 RRF，不影响可用性。
- 关键词检索用 `ILIKE` 简单实现，生产建议换 FTS/trigram 或 BM25。
