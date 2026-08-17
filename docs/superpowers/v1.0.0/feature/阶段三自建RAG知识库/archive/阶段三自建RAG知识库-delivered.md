# 阶段三自建RAG知识库 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

实现手写完整 RAG 链路：PDF/TXT/MD 上传解析 → 固定窗口切片（chunk_size/overlap）→ Embedding 向量化 → Qdrant 手动入库 → 相似度检索（TopK + 阈值）→ RAG Prompt 组装 → 流式问答。前端新增上传/文档管理页与聊天页“知识库”开关。真实 Embedding API 受智谱余额限制，提供 `EMBEDDING_MODE=local` 本地哈希向量兜底，链路已端到端实测。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/services/chunker.py`、`local_embedding.py`、`document_service.py` |
| 新增 | `backend/app/repositories/document_repo.py`、`vector_repo.py` |
| 新增 | `backend/app/api/documents.py`、`backend/app/schemas/document.py` |
| 改 | `backend/app/models/entities.py`（Document 表） |
| 改 | `backend/app/adapters/model_adapter.py`（embed_texts + local 模式） |
| 改 | `backend/app/db/qdrant.py`（按 embedding_dimensions 建/重建集合） |
| 改 | `backend/app/services/chat_service.py`、`backend/app/schemas/chat.py`（use_rag） |
| 改 | `backend/app/main.py`、`backend/app/core/config.py`、`.env*`、`requirements.txt` |
| 新增 | `backend/tests/test_rag.py` |
| 改 | `frontend/src/views/UploadView.vue`、`ChatView.vue`、`frontend/src/api/chatStream.ts` |
| 新增 | `docs/learning/阶段3/01~05` 共 5 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段三自建RAG知识库/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 上传 TXT/MD/PDF 成功，PG 有元信息，Qdrant 有切片向量。
- [x] 切片满足 chunk_size/overlap 约束。
- [x] 检索能按 TopK + 阈值返回相关片段。
- [x] 开启知识库问答后，回答内容基于上传文档。
- [x] 前端可上传、查看、删除文档，聊天可开关知识库。
- [x] `pytest -q`（21 passed）与 `pnpm build` 通过。
- [x] 学习文档 5 篇齐全且五小节完整。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无文档时 Qdrant 无向量、上传页空态；有文档时列表与检索正常 |
| 常量/mock/真数据 | 通过 | 切片/检索为真实代码；单测 mock Embedding/Qdrant；容器实测用 local 向量真跑全链路 |
| 多入口 | 通过 | 上传页与聊天开关共用同一套后端文档/检索服务；use_rag=false 保持普通聊天 |
| 失败/缺省 | 通过 | 空文件/不支持格式/无文本/超 5MB 均返回明确错误；Embedding 无额度时 local 模式可兜底 |

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

- 后端测试：`pytest -q` → 21 passed（切片、RAG Prompt、上传接口、本地向量、既有持久化）。
- 前端构建：`pnpm build` 通过。
- Docker 实测：上传 `知识库.txt` 返回 200，PG `documents` 有元信息，Qdrant `document_vectors` points_count=1、size=1024；`use_rag=true` 流式问答返回 200 且回答包含“红色”等内容。
- 学习文档：`docs/learning/阶段3/01~05` 五篇齐全，均为五小节结构。

## 遗留风险

- 真实 Embedding 已切换为硅基流动 `BAAI/bge-m3`（`EMBEDDING_MODE=api`）并实测通过；若 Key 到期或额度用尽需更换。
- `local` 哈希向量保留为开发兜底，仅用于无 Embedding 额度时演示链路，语义质量有限。
- 切片器为固定窗口实现，后续可升级为按句/段落智能切片。
- PDF 扫描件无文字层时无法提取，OCR 不在本阶段范围。
