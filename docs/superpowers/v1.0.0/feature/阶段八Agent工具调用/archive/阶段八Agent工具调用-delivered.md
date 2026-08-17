# 阶段八Agent工具调用 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

实现 Function Calling Agent：工具注册中心（时间/计算器/知识库检索/文档列表）、适配层 tool_calls 解析、chat_service Agent 循环、SSE tool_start/tool_done、前端“工具”开关与调用提示。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/tools/__init__.py`、`base.py`、`registry.py`、`builtin.py` |
| 改 | `backend/app/adapters/model_adapter.py`（tools/tool_calls） |
| 改 | `backend/app/services/chat_service.py`（Agent 循环） |
| 改 | `backend/app/schemas/chat.py`、`backend/app/api/chat.py`（use_tools） |
| 改 | `backend/app/core/config.py`、`.env*`（tools 配置） |
| 新增 | `backend/tests/test_tools.py` |
| 改 | `frontend/src/api/chatStream.ts`、`frontend/src/views/ChatView.vue`（工具开关/提示） |
| 新增 | `docs/learning/阶段8/01~03` 共 3 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段八Agent工具调用/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 工具注册中心可列出 OpenAI 格式 tools。
- [x] 计算器安全计算，不执行任意代码。
- [x] 聊天开启工具后能调用时间/计算器并基于结果回答。
- [x] SSE 输出 tool_start/tool_done。
- [x] 工具失败不阻塞聊天。
- [x] `pytest -q`（30 passed）与 `pnpm build` 通过。
- [x] 学习文档 3 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无工具调用直接回答；有调用输出 tool_start/done |
| 常量/mock/真数据 | 通过 | 单测覆盖计算器/注册；容器实测真实调用 GLM 工具链路 |
| 多入口 | 通过 | 普通聊天/知识库/工具共用 chat 链路，use_tools 开关控制 |
| 失败/缺省 | 通过 | 参数解析失败兜底；工具不存在返回提示；最大轮数防死循环 |

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

- 后端测试：`pytest -q` → 30 passed。
- 前端构建：`pnpm build` 通过。
- Docker 实测：开启工具问“2+3*4”，SSE 输出 `tool_start calculator` → `tool_done 2+3*4 = 14` → 最终回答，chat 200。
- 学习文档：`docs/learning/阶段8/01~03`。

## 遗留风险

- 仅支持同步工具调用，网页搜索/浏览器工具未接入（后续可扩展）。
- 模型对工具的选择依赖提示词与参数质量，可能需要微调。
- 工具执行无超时/并发限制，阶段 10 异步化时补充。
