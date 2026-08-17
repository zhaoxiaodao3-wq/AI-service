# 01 · 业务数据建模与 SQLAlchemy 实体

## 做了什么

阶段 2 新增四张业务表，全部通过 SQLAlchemy ORM 定义在 `backend/app/models/entities.py`：

- `users`：用户表，包含用户名、密码哈希、创建时间。
- `ai_models`：AI 模型配置表，包含模型名、厂商、BaseURL、加密后的 API Key、启用状态、权重。
- `chat_sessions`：会话表，通过 `user_id` 外键归属用户，记录标题、模型与创建/更新时间。
- `chat_messages`：消息表，通过 `session_id` 外键归属会话，记录角色、内容、Token 消耗与创建时间。

## 为什么

阶段 1 的会话和消息存在前端内存里，刷新页面就丢；模型清单写在 `.env` 静态配置里，改模型要改代码。把它们建模成数据库表后，数据可以被持久化、被接口查询，也为阶段 3/4 的 RAG 与长期记忆提供“业务数据底座”。

## 原理

### ORM 映射

每张表对应一个继承 `Base` 的 Python 类，字段用 `Mapped[...]` 和 `mapped_column(...)` 声明。例如：

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="新会话")
```

`__tablename__` 决定数据库里的表名，字段类型用 `String`、`Integer`、`Text`、`Boolean`、`DateTime` 等通用类型，保证 PostgreSQL 和测试用 SQLite 都能跑。

### 外键与关系

- `ChatSession.user_id → users.id`：一个用户拥有多个会话。
- `ChatMessage.session_id → chat_sessions.id`：一个会话包含多条消息。
- `relationship(back_populates=...)` 让 ORM 两侧能互相访问，例如 `session.messages` 直接得到该会话全部消息。
- `cascade="all, delete-orphan"`：删除会话时自动删除其下消息，避免孤儿数据。

### 删除策略

数据库外键用 `ondelete="CASCADE"`，ORM 关系再用 `cascade` 双保险。SQLite 默认不强制外键，但删除会话时 ORM 仍会先删子消息，所以测试和 PostgreSQL 行为一致。

## 命令解释

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest -q
```

运行全部后端测试。`tests/test_persistence.py` 使用 SQLite 内存库验证会话 CRUD、消息查询、模型列表与聊天持久化。

```powershell
docker exec aigc-postgres psql -U aigc_user -d aigc_chat -c "\dt"
```

查看 PostgreSQL 中已经创建的表，应能看到 `users`、`ai_models`、`chat_sessions`、`chat_messages`。

## 避坑

- 业务“会话”与 SQLAlchemy 的 `Session` 同名，实体命名用 `ChatSession` 避免混乱。
- SQLite 内存库每次连接默认是独立库，测试必须加 `StaticPool`，否则建表连接和业务连接各玩各的，报 `no such table`。
- `datetime.utcnow()` 有弃用告警，后续可换成 timezone-aware 的 `datetime.now(datetime.UTC)`。
- 实体字段类型尽量用通用类型，避免测试环境与生产环境行为不一致。
