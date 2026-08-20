# 阶段十一LLM安全防护增强 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-20
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

将安全防护从“只防用户输入”升级为多层：输入规范化 + 启发式 + 可选 LLM 复核；上传文档切片、检索片段、工具输出全部过注入扫描；RAG Prompt 使用 `<documents>` 数据边界。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/services/guard_service.py` |
| 改 | `backend/app/services/security_service.py`（normalize_input） |
| 改 | `backend/app/services/chat_service.py`（guard 接入） |
| 改 | `backend/app/services/document_processing.py`（入库过滤） |
| 改 | `backend/app/services/retrieval_service.py`（召回过滤） |
| 改 | `backend/app/tools/registry.py`（工具输出扫描） |
| 改 | `backend/app/services/document_service.py`（数据边界） |
| 改 | `backend/app/core/config.py`、`.env*` |
| 改 | `backend/tests/test_security.py` |
| 新增 | `docs/learning/阶段11/04-LLM安全防护增强.md` |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段十一LLM安全防护增强/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 用户输入规范化 + 启发式拦截。
- [x] llm_judge 模式可用，失败回退。
- [x] 上传注入文档被过滤/任务失败。
- [x] 检索片段注入不入 Prompt。
- [x] 工具结果注入被过滤。
- [x] `pytest -q`（36 passed）与 `pnpm build` 通过。
- [x] 学习文档 1 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 正常文档 completed；注入文档 failed |
| 常量/mock/真数据 | 通过 | 测试覆盖规范化/guard；容器实测上传与 chat |
| 多入口 | 通过 | 用户/文档/检索/工具共用 security_service |
| 失败/缺省 | 通过 | guard 失败回退 safe；文档全过滤任务失败 |

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

- 后端测试：`pytest -q` → 36 passed。
- 前端构建：`pnpm build` 通过。
- Docker 实测：
  - 正常文档任务 completed。
  - 注入文档任务 failed，error=“文档包含可疑注入内容，已拦截”。
  - 聊天输入注入返回 `prompt_injection`。
- 学习文档：`docs/learning/阶段11/04-LLM安全防护增强.md`。

## 遗留风险

- 启发式为正则黑名单，复杂对抗需接 Llama Guard 或专用网关。
- LLM 复核使用免费 GLM，会多一次模型调用与延迟。
- 工具结果扫描目前只覆盖已注册工具，未来新增 URL/网页工具需接入同一 `execute_tool`。
