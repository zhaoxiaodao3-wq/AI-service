# 05 · Docker 内建表与种子数据

## 做了什么

FastAPI 启动时通过 `lifespan` 调用 `init_db()`：

- 自动执行 `Base.metadata.create_all(engine)` 建表。
- 创建默认用户 `local`（id=1）。
- 从 `.env` 的静态模型清单种入 `ai_models`，API Key 加密后写入。
- 重复启动不会重复插入（幂等）。

## 为什么

阶段 1 后端容器化后，数据库表如果还要手动执行脚本，部署和本地体验都会变差。放进应用生命周期后，`docker compose up -d --build` 一条命令就能把“建表 + 种子数据 + 启动服务”全部做完，符合“一键启动整套”的目标。

## 原理

### FastAPI lifespan

```python
@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)
```

服务启动时先初始化数据库，再开始接收请求。Docker backend 服务 `depends_on` PostgreSQL healthy，保证数据库可用后才启动。

### 幂等种子

```python
if db.query(User).filter_by(username="local").first() is None:
    db.add(User(username="local", password_hash=""))

existing = {m.name for m in db.query(AiModel).all()}
for weight, name in enumerate(s.models):
    if name not in existing:
        db.add(AiModel(...))
```

每次都先查是否存在，存在就跳过，因此容器重启不会产生重复用户/模型。

## 命令解释

```powershell
docker compose up -d --build backend
```

重建并启动后端容器；启动时自动建表并种数据。

```powershell
docker exec aigc-postgres psql -U aigc_user -d aigc_chat -c "SELECT id, username FROM users;"
```

确认默认用户已创建。

```powershell
docker exec aigc-postgres psql -U aigc_user -d aigc_chat -c "SELECT name, api_key_encrypted FROM ai_models ORDER BY weight;"
```

确认模型已种入且 Key 为密文。

## 避坑

- 生产环境不要依赖 `create_all` 做表结构升级，阶段 6 前应引入 Alembic 迁移。
- `SECRET_KEY` 必须通过 `.env` 注入，不能把开发默认值用于生产。
- 模型种子只导入一次；后续想改模型配置应直接改数据库或阶段 5 的管理接口。
- 如果数据库还没 healthy 就启动 backend，`depends_on` 会等待，但网络抖动时建议再观察容器日志。
