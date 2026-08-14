# 阶段二业务数据全持久化 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 1 会话和消息都在前端内存里，刷新即丢失；模型清单是静态配置。本阶段补齐 SQLAlchemy 实体、建表与种子数据、会话/消息/模型 CRUD，并在聊天流中自动保存每轮对话，API Key 使用 Fernet 加密落库。

## 设计

### 1. 数据库实体（`backend/app/models/entities.py`）

全部使用通用 SQLAlchemy 类型，兼容 PostgreSQL 与测试用 SQLite：

- `User`：`id`、`username`（unique）、`password_hash`、`created_at`。
- `AiModel`：`id`、`name`（unique）、`provider`、`base_url`、`api_key_encrypted`、`enabled`、`weight`、`created_at`。
- `ChatSession`：`id`、`user_id` FK、`title`、`model`、`created_at`、`updated_at`。
- `ChatMessage`：`id`、`session_id` FK、`role`、`content`、`token_count`、`created_at`。

`Base` 放在 `backend/app/db/base.py`。

### 2. 初始化与种子

`backend/app/db/init_db.py`：

- `Base.metadata.create_all(engine)` 建表。
- 创建默认用户 `local`（id=1，无登录场景，密码哈希占位）。
- 从 `Settings.models` 种子模型配置，API Key 使用加密存储；重复运行幂等。
- FastAPI lifespan 启动时调用；Docker backend 自动执行。

### 3. 安全加密（`backend/app/core/security.py`）

- `Settings` 新增 `secret_key`（默认开发值，`.env.example` 同步）。
- `encrypt_secret` / `decrypt_secret` 基于 `cryptography.fernet.Fernet`。

### 4. 仓库与服务

- `backend/app/repositories/session_repo.py`、`message_repo.py`、`model_repo.py`、`user_repo.py`。
- `backend/app/services/session_service.py`、`message_service.py`、`model_service.py`。
- 统一默认用户 id=1。

### 5. 接口

`backend/app/api/sessions.py`：

- `GET /api/sessions`：列出默认用户会话（按 updated_at 倒序）。
- `POST /api/sessions`：新建会话，可选 `title`/`model`。
- `GET /api/sessions/{id}/messages`：查询会话消息（按创建时间正序）。
- `PATCH /api/sessions/{id}`：重命名（`title`）。
- `DELETE /api/sessions/{id}`：删除会话及其消息。

`backend/app/api/models.py` 改为读数据库启用模型；数据库为空时回退 `Settings.models`。

### 6. 聊天自动持久化

- `ChatStreamRequest` 增加 `session_id: int | None`。
- 传 `session_id` 时：流开始前保存最后一条用户消息；流结束后保存完整 AI 回复；错误时保存错误文案。
- 不传 `session_id` 保持原行为，兼容既有测试与调用。

### 7. 前端

- `chatStream.ts` 支持 `sessionId`，请求体带 `session_id`。
- `ChatView.vue`：
  - 挂载时拉取 `/sessions`，无会话自动创建。
  - 新建/切换会话调用后端；切换时加载历史消息。
  - 会话项支持重命名（`ElMessageBox.prompt`）与删除（确认框）。
  - 发送时携带 `session_id`，后端自动保存消息。

### 8. 测试

新增 `backend/tests/test_persistence.py`，使用 SQLite 内存库 + 依赖覆盖：

- 会话 CRUD（创建/列表/重命名/删除）。
- 消息保存与查询。
- 模型列表从数据库返回。
- chat 流带 session_id 时自动保存 user/assistant 消息。

## 验收标准

- [x] 四张表创建成功，默认用户与模型种子幂等。
- [x] API Key 在数据库中为密文，能解密回原值。
- [x] 会话/消息/模型接口全部可用并测试通过。
- [x] 聊天带 session_id 时自动保存每轮消息。
- [x] 前端刷新后历史会话与消息不丢失。
- [x] `pytest -q` 通过（17 passed），`pnpm build` 通过。
- [x] Docker backend 重建后接口在容器内可用。

## 非目标

- 不做登录/注册/鉴权（阶段 5）。
- 不改 SSE 协议。
- 附件不持久化（阶段 3/4 再处理）。
