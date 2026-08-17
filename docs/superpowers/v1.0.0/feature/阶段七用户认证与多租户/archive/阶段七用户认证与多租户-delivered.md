# 阶段七用户认证与多租户 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

加入用户注册/登录/JWT/刷新令牌/登出，密码 bcrypt 哈希；会话、文档、聊天记忆全部改为当前用户维度；前端新增登录页、路由守卫、Token 拦截器与退出按钮；提供 local 数据迁移脚本。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/api/auth.py`、`backend/app/api/deps.py`、`backend/app/schemas/auth.py` |
| 改 | `backend/app/core/security.py`（bcrypt + JWT）、`backend/app/models/entities.py`（RefreshToken） |
| 改 | `backend/app/core/config.py`、`backend/requirements.txt`、`.env*` |
| 改 | `backend/app/api/sessions.py`、`documents.py`、`chat.py`、`services/*`（用户隔离） |
| 新增 | `backend/scripts/migrate_local_data.py` |
| 新增 | `backend/tests/test_auth.py`，更新 `test_persistence.py`、`test_rag.py`、`test_chat_stream.py`、`test_access_log.py` |
| 新增 | `frontend/src/views/LoginView.vue` |
| 改 | `frontend/src/router/index.ts`、`frontend/src/api/request.ts`、`frontend/src/layouts/MainLayout.vue` |
| 新增 | `docs/learning/阶段7/01~04` 共 4 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段七用户认证与多租户/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 注册/登录/刷新/登出/me 全链路可用。
- [x] 两个用户互不可见会话/文档/记忆。
- [x] 未登录访问业务接口返回 401。
- [x] 密码为 bcrypt 密文。
- [x] 前端登录后可进入聊天/上传，退出后跳登录。
- [x] `pytest -q`（27 passed）与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 新用户无会话/文档；注册后正常创建 |
| 常量/mock/真数据 | 通过 | 测试用 SQLite + 依赖覆盖；真实 JWT/bcrypt |
| 多入口 | 通过 | 会话/文档/记忆统一走当前用户 ID |
| 失败/缺省 | 通过 | 未登录 401；越权访问 404；刷新令牌轮换与登出撤销 |

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

- 后端测试：`pytest -q` → 27 passed（注册/登录/刷新/登出/me、用户隔离、401、既有功能）。
- 前端构建：`pnpm build` 通过。
- 迁移脚本：`python -m scripts.migrate_local_data --username <user>`。
- 学习文档：`docs/learning/阶段7/01~04`。

## 遗留风险

- 前端 Token 使用 localStorage，生产建议换 HttpOnly Cookie 降低 XSS 风险。
- 旧 `local` 用户的数据需手动运行迁移脚本；Qdrant 中 `user_id=1` 的记忆向量需后续脚本或重新生成。
- stats 与模型配置暂未按用户隔离（阶段 12 细化）。
