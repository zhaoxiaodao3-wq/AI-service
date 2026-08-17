# 阶段四AI长期向量记忆 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

实现 AI 长期向量记忆：每轮对话结束自动生成记忆文本并写入 Qdrant `memory_vectors`；新提问自动检索历史记忆（排除当前会话，TopK + 阈值降噪），与短期上下文、知识库片段一起注入 Prompt，完成双层记忆融合。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `backend/app/repositories/vector_repo.py`（upsert/search/delete memory） |
| 改 | `backend/app/services/chat_service.py`（session_id 记忆召回） |
| 改 | `backend/app/services/document_service.py`（build_rag_messages 支持 memories） |
| 改 | `backend/app/api/chat.py`（流结束后自动写记忆） |
| 改 | `backend/app/core/config.py`、`.env*`（memory 配置） |
| 改 | `backend/tests/test_rag.py`、`backend/tests/test_persistence.py` |
| 新增 | `docs/learning/阶段4/01~04` 共 4 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段四AI长期向量记忆/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 每轮对话结束自动写入一条记忆向量。
- [x] 新会话提问可召回上一会话的记忆并影响回答。
- [x] 当前会话记忆不重复注入（排除 session_id）。
- [x] 低于阈值的无关记忆不注入。
- [x] 与知识库问答可同时生效。
- [x] `pytest -q`（22 passed）与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无记忆时检索为空不注入；有记忆时正常注入并影响回答 |
| 常量/mock/真数据 | 通过 | 测试 mock 记忆网络；容器实测用真实 Embedding 写入并召回 |
| 多入口 | 通过 | 普通聊天/知识库/记忆共用一套 chat 链路，session_id 控制记忆开关 |
| 失败/缺省 | 通过 | 记忆写入失败仅 warning；检索阈值过滤低分记忆；无 session_id 不写记忆 |

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

- 后端测试：`pytest -q` → 22 passed（记忆 Prompt、记忆网络 mock、既有持久化/RAG）。
- 容器实测（真实 Embedding）：
  - 会话 A：`我的名字是小明，请记住我` → AI 回答记住。
  - 会话 B：`我叫什么名字？` → AI 回答“你的名字是小明”。
  - Qdrant `memory_vectors` points_count=2，payload 为两轮对话记忆文本。
- 学习文档：`docs/learning/阶段4/01~04` 四篇齐全。

## 遗留风险

- 记忆写入依赖 Embedding API，网络/额度异常时记忆会丢，但聊天不受影响。
- 目前没有记忆编辑/删除界面；`delete_session_memories` 已提供函数，删除会话接口暂未联动。
- 记忆相似度阈值按默认 0.35，后续可按真实 score 调优。
