# 阶段一：基础 AI 对话 + 多模型对接 + 短期记忆 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-13
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

完成阶段一核心对话链路：统一 `ModelAdapter` 二次封装 LiteLLM（官方直连 / 中转双模式）、`GET /api/models` 模型清单接口、`POST /api/chat/stream` SSE 流式对话接口、短期上下文拼接与 Token 截断、前端聊天页流式打字与豆包风格布局（左侧会话菜单 + 右侧聊天区 + 文件/图片上传），并补齐异常容错与 6 篇学习文档。真实联调使用智谱 GLM-4-Flash 验证逐段中文输出与错误分支。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/adapters/model_adapter.py`（ChatRequest/ChatResponse/ModelError/chat/stream_chat） |
| 新增 | `backend/app/api/models.py`、`backend/app/api/chat.py` |
| 新增 | `backend/app/schemas/chat.py`、`backend/app/services/chat_service.py`、`backend/app/services/context_builder.py` |
| 修改 | `backend/app/api/router.py`、`backend/app/core/config.py`（模型清单、max_context_tokens） |
| 新增 | `backend/tests/test_model_adapter.py`、`test_models.py`、`test_chat_stream.py`、`test_context_builder.py` |
| 新增 | `frontend/src/api/chatStream.ts`（fetch + ReadableStream 解析 SSE） |
| 修改 | `frontend/src/views/ChatView.vue`（会话/流式渲染/模型下拉/附件/错误态） |
| 修改 | `frontend/package.json`、`pnpm-lock.yaml`（`@element-plus/icons-vue`） |
| 新增 | `docs/learning/阶段1/01~06` 共 6 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段一基础对话多模型适配/`（requirements/specs/plans/archive） |

## 验收结果

### 适配器

- [x] `chat` 与 `stream_chat` 均实现，且不裸调 LiteLLM 以外的模型接口。
- [x] 官方/中转两种模式可在 `.env` 切换，无需改代码（`_resolve_credentials` 中转优先）。
- [x] 未配置 Key 时调用返回明确 `ModelError(invalid_key)`，不崩溃。

### 接口

- [x] `GET /api/models` 返回模式、模型列表、默认模型。
- [x] `POST /api/chat/stream` 返回 `text/event-stream`，含 delta/done/error 事件。
- [x] 有 Key 时实测流式返回内容：2026-08-13 使用智谱 GLM-4-Flash 逐段中文输出，修复 `openai/` 前缀与流式 await 问题后全链路正常（commit `b1c08fd`）。

### 上下文截断

- [x] 短对话原样透传；超长对话自动删除最早消息，system prompt 保留。
- [x] token 估算函数对中文/英文均有合理估算（tiktoken 优先，字符估算兜底）。

### 前端

- [x] 聊天页可发送并流式显示 AI 回复（打字效果）。
- [x] 多轮连续对话可正常进行。
- [x] 模型下拉可切换并生效。
- [x] 错误事件显示友好提示，不白屏。
- [x] 页面为左侧菜单 + 右侧聊天区布局（豆包风格）。
- [x] 新会话/历史会话切换正常。
- [x] 输入框支持上传文件与图片并展示附件，附件随消息携带，后端不报错。

### 文档与注释

- [x] `docs/learning/阶段1/` 6 篇文档齐全且五小节完整（做了什么/为什么/原理/命令解释/避坑）。
- [x] 所有新增代码注释符合规范（方法 docstring、逻辑块注释、不直观行行内注释）。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 新会话为空消息列表；发送后会话内回显用户与 AI 消息，切换会话可恢复内存态 |
| 常量/mock/真数据 | 通过 | 模型清单与 `MAX_CONTEXT_TOKENS` 来自 `Settings`；单测 mock LiteLLM 不发真实请求；真实流式链路用智谱 GLM-4-Flash 联调 |
| 多入口 | 通过 | 官方/中转双模式由 `_resolve_credentials` 统一选择，切换只改 `.env`，不改代码 |
| 失败/缺省 | 通过 | 未配置 Key/错误 Key/超时/断流统一映射 `ModelError` → SSE `error` 事件，前端错误气泡并恢复输入 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。页面布局按原始需求第 5.9 节的豆包风格示意实现（左侧会话菜单 + 右侧聊天区 + 底部上传/输入区），已逐项验收。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告
- [x] commit 前 validate-harness 已跑

## 验证证据

- 后端：`backend\venv\Scripts\python.exe -m pytest -q` → 11 passed（适配层 mock、模型列表、SSE 事件序列、上下文截断）。
- 前端：`pnpm build` → `vue-tsc -b && vite build` 通过，产物生成于 `frontend/dist/`。
- 真实联调：`.env` 配置智谱 GLM-4-Flash 后 `POST /api/chat/stream` 逐段返回 `delta` 并以 `done` 结束；错误 Key 返回 `error: invalid_key`。

## 遗留风险

- 会话与附件仅存前端内存，刷新页面丢失，阶段 2 持久化到 PostgreSQL。
- 附件阶段 1 只上传展示，不做解析；图片多模态理解后续阶段接入。
- Element Plus 全量引入导致前端打包体积偏大（阶段 5 改按需引入）。
- `fastapi.testclient` 有 Starlette 弃用警告，不影响功能（后续可切换 httpx2）。
- 真实流式联调依赖本地 `backend/.env` 中的 Key，Key 不提交仓库；无 Key 环境只能验证错误分支。
