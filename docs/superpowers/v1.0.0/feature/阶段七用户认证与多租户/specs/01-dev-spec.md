# 阶段七用户认证与多租户 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

当前所有业务数据挂在默认 `local` 用户下，无法多用户隔离。本阶段加入注册/登录/JWT/刷新令牌，并把会话/文档/记忆改为“当前用户”维度。

## 设计

### 1. 配置与依赖

`Settings` 新增：

- `jwt_secret`、`jwt_algorithm=HS256`
- `access_token_expire_minutes=60`
- `refresh_token_expire_days=7`

新增依赖：`PyJWT`、`bcrypt`。

### 2. 数据模型

- `User.password_hash` 存 bcrypt 哈希。
- 新增 `RefreshToken` 表：`user_id`、`token_hash`、`expires_at`、`revoked`。

### 3. 认证接口

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`

注册/登录返回 access + refresh；刷新时轮换 refresh；登出时撤销 refresh。

### 4. 当前用户依赖

新增 `backend/app/api/deps.py` 的 `get_current_user`：

- 解析 `Authorization: Bearer <token>`
- 校验过期与用户存在
- 失败返回 401

### 5. 多租户隔离

- sessions API：全部改为当前用户 ID。
- documents API：上传/列表/删除按当前用户。
- chat：session 校验、消息持久化、记忆写入/召回使用当前用户 ID。
- stats：保持全局统计（阶段 12 再细化）。
- model 配置：保持全局。

### 6. 旧数据迁移

新增 `backend/scripts/migrate_local_data.py`：把 `user_id=1` 的数据迁移到指定用户名。

### 7. 前端

- 新增 `/login` 登录/注册页。
- 路由守卫：未登录跳登录。
- `request.ts` 自动携带 Token，401 跳登录。
- 顶栏显示当前用户与退出按钮。

## 验收标准

- [x] 注册/登录/刷新/登出/me 全链路可用。
- [x] 两个用户互不可见会话/文档/记忆。
- [x] 未登录访问业务接口返回 401。
- [x] 密码为 bcrypt 密文。
- [x] 前端登录后可进入聊天/上传，退出后跳登录。
- [x] `pytest -q` 与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 非目标

- 不做邮箱验证/找回密码/第三方登录。
- stats 与模型配置暂不做用户隔离。
