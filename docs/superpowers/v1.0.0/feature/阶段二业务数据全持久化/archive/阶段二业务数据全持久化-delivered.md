# 阶段二业务数据全持久化 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-14
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

阶段 1 的会话和消息都在前端内存里，模型清单是静态配置。本阶段新增用户/模型/会话/消息四张表，实现会话 CRUD、消息保存与查询、模型动态加载，API Key 使用 Fernet 加密落库；聊天流携带 `session_id` 时自动保存每轮消息，前端刷新后历史会话不丢失。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/db/base.py`、`backend/app/models/entities.py` |
| 新增 | `backend/app/core/security.py`、`backend/app/db/init_db.py` |
| 新增 | `backend/app/repositories/`（user/session/message/model） |
| 新增 | `backend/app/services/`（session/message/model） |
| 新增 | `backend/app/schemas/session.py`、`backend/app/api/sessions.py` |
| 改 | `backend/app/api/router.py`、`backend/app/api/models.py` |
| 改 | `backend/app/api/chat.py`、`backend/app/schemas/chat.py`（session_id 自动持久化） |
| 改 | `backend/app/core/config.py`、`backend/app/core/exceptions.py`、`backend/app/main.py` |
| 新增 | `backend/tests/test_persistence.py` |
| 改 | `backend/tests/test_models.py`、`backend/tests/test_access_log.py` |
| 改 | `frontend/src/api/chatStream.ts`、`frontend/src/views/ChatView.vue` |
| 改 | `.env.example`、`backend/.env.example`（SECRET_KEY） |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段二业务数据全持久化/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 四张表创建成功，默认用户与模型种子幂等。
- [x] API Key 在数据库中为密文，能解密回原值。
- [x] 会话/消息/模型接口全部可用并测试通过。
- [x] 聊天带 session_id 时自动保存每轮消息。
- [x] 前端刷新后历史会话与消息不丢失。
- [x] `pytest -q` 通过（17 passed），`pnpm build` 通过。
- [x] Docker backend 重建后接口在容器内可用。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无会话时前端自动创建；空会话显示空态；有消息按序加载 |
| 常量/mock/真数据 | 通过 | 模型列表从 `ai_models` 读取，空表回退 Settings；API Key 为真实加密值 |
| 多入口 | 通过 | 本地 uvicorn 与 Docker 共用同一套实体/仓库/服务；chat 无 session_id 保持原行为 |
| 失败/缺省 | 通过 | 会话不存在返回 404；前端请求失败回退本地会话保持页面可用；删除/重命名带确认与取消 |

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

- 后端测试：`pytest -q` → 17 passed（会话 CRUD、消息查询、模型列表、chat 自动持久化、加密回环）。
- 前端构建：`pnpm build` → `vue-tsc -b && vite build` 通过。
- Docker 实测：`POST /api/sessions` → `GET /api/sessions` → `PATCH` → `DELETE` 全部 200；`GET /api/models` 返回数据库模型清单；带 `session_id` 的流式对话后 `GET /api/sessions/{id}/messages` 返回 `user` 与 `assistant` 两条消息。
- API Key 加密：`psql` 查询 `ai_models.api_key_encrypted` 为 Fernet 密文，非明文。
- 前端持久化：无头浏览器发送消息后刷新页面，历史用户消息仍从后端加载显示。

## 遗留风险

- 登录/鉴权未做（阶段 5），目前所有会话挂在默认用户 `local`（id=1）下。
- 附件未持久化（阶段 3/4 再处理）。
- 模型配置仍以 `.env` 单 Key 种子导入，多模型独立 Key 管理留到阶段 5。
- `datetime.utcnow` 有弃用告警，后续可切 timezone-aware datetime（不影响功能）。
