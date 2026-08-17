# 01 · 认证架构与 JWT

## 做了什么

阶段 7 加入用户注册/登录，访问令牌使用 JWT：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

登录后前端把 `access_token` 放进 `Authorization: Bearer <token>`，后端通过 `get_current_user` 解析当前用户。

## 为什么

没有账号体系，会话/文档/记忆都只能挂在同一个本地用户下，无法多用户隔离，也无法上线。JWT 是当前最主流的无状态认证方案，适合前后端分离项目。

## 原理

### JWT 结构

```text
Header.Payload.Signature
```

Payload 里放 `sub`（用户 ID）和 `exp`（过期时间），服务端用 `JWT_SECRET` 签名。每次请求只需验签，不需要查会话表。

### 认证依赖

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    ...
```

业务接口加 `user: User = Depends(get_current_user)` 即可拿到当前用户。

## 命令解释

```powershell
$body = '{"username":"alice","password":"secret123"}'
Invoke-RestMethod -Uri http://localhost:8000/api/auth/register -Method Post -ContentType "application/json" -Body $body
```

返回 `access_token` 与 `refresh_token`。

## 避坑

- `JWT_SECRET` 生产必须换成强随机值。
- Token 不要放 cookie 以外的地方时明文存储；本项目开发用 localStorage，生产建议 HttpOnly Cookie。
- 业务接口必须加认证依赖，否则等于没隔离。
