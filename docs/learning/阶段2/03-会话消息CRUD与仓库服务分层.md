# 03 · 会话消息 CRUD 与仓库服务分层

## 做了什么

新增完整的会话与消息接口：

```text
GET    /api/sessions              列出会话
POST   /api/sessions              新建会话
GET    /api/sessions/{id}/messages 查询历史消息
PATCH  /api/sessions/{id}         重命名
DELETE /api/sessions/{id}         删除会话（连消息）
```

实现按 `api → service → repository` 分层，并新增 `GET /api/models` 从数据库读取启用模型。

## 为什么

分层的目的：

- API 层只负责 HTTP 参数、状态码和响应格式。
- Service 层负责业务规则（默认用户、默认标题、404 判断）。
- Repository 层只做数据库增删改查，方便单测和以后替换实现。

这样每个文件职责单一，阶段 3/4 新增 RAG 和记忆时可以直接复用。

## 原理

### FastAPI 依赖注入

```python
def list_sessions(db: Session = Depends(get_db)):
    sessions = session_service.list_sessions(db)
    return ok({"sessions": [...]})
```

`Depends(get_db)` 让 FastAPI 为每个请求创建数据库会话，请求结束自动关闭，不用手写 try/finally。

### 仓库层

`session_repo.py` 只做 SQL 操作：

```python
def list_sessions(db, user_id):
    return db.query(ChatSession).filter_by(user_id=user_id).order_by(ChatSession.updated_at.desc()).all()
```

`message_repo.add_message` 在写入消息后刷新会话的 `updated_at`，让活跃会话排到列表前面。

### 统一响应

接口统一返回 `{code: 0, message: "ok", data: {...}}`，前端 `request.ts` 拦截器只处理 `data`，格式一致。

### 404 处理

`AppError` 支持 `http_status`，`session_service.get_session` 找不到会话时抛 `AppError(404, "会话不存在")`，全局异常处理器返回 HTTP 404。

## 命令解释

```powershell
$body = '{"title":"测试会话"}'
Invoke-RestMethod -Uri http://localhost:8000/api/sessions -Method Post -ContentType "application/json" -Body $body
```

新建会话。返回体里带 `id`，后续查询消息、重命名、删除都靠它。

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/sessions/1/messages
```

查询会话 1 的历史消息。

## 避坑

- `POST /api/sessions` 即使所有字段可选，也要传 `{}` 作为 JSON body，否则 FastAPI 返回 422。
- 会话查询必须带 `user_id` 过滤，避免阶段 5 做多用户时跨用户看到别人会话。
- 删除会话依赖 ORM `cascade`，测试里要验证消息一并删除。
- 时间排序统一用 `updated_at DESC`，否则刚聊过的会话不会排到前面。
