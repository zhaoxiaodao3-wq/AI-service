# 01 · Alembic 数据库迁移（给数据库装上"版本管理"）

## 这一步做了什么

把数据库建表方式从"启动时 `create_all`"升级为 **Alembic 迁移**：

- 新增 `backend/alembic/` 迁移目录 + `alembic.ini` 配置
- 生成初始迁移 `0001_initial`：一次性建出全部 9 张业务表
- 启动流程改为 `alembic upgrade head`（自动迁移到最新版本）
- 兼容兜底：alembic 不可用时回退 `create_all`，开发环境不阻塞

## 为什么要这么做（用盖楼打比方）

`create_all` 的致命问题是：**它只负责"第一次建表"，不会改表**。

假设上线后你加了一个字段 `users.avatar`：

- `create_all` 看到 users 表已经存在 → **什么都不做** → 新代码查 avatar 直接报错
- 你得手动写 `ALTER TABLE users ADD COLUMN avatar ...` 去改生产库
- 改了生产库，测试库、同事的本地库、新服务器又没改 → 到处不一致

Alembic 就是数据库的 **git**：

```text
create_all 时代：  房子盖好了就不能再动（改不了结构）
Alembic 时代：     每次改结构都留一个"版本记录"，upgrade 升级、downgrade 回滚
```

| 概念 | 对应 git | 对应 Alembic |
|------|----------|--------------|
| 版本文件 | commit | `alembic/versions/0001_initial.py` |
| 升级 | git merge 到新版本 | `alembic upgrade head` |
| 回滚 | git revert | `alembic downgrade base` |
| 当前版本 | HEAD | `alembic_current` 表里记录 |

## 底层原理

### 1. 迁移文件长什么样（backend/alembic/versions/0001_initial.py）

每个迁移文件是一个 Python 脚本，定义两个函数：

```python
def upgrade() -> None:
    op.create_table("users", ...)      # 升级时执行：建表
    op.create_table("chat_sessions", ...)
    ...

def downgrade() -> None:
    op.drop_table("chat_sessions")     # 回滚时执行：删表（倒序）
    op.drop_table("users")
```

- `upgrade()`：把数据库从"上一个版本"变成"这个版本"
- `downgrade()`：把数据库从"这个版本"退回"上一个版本"（可逆性保证）
- 表创建顺序很重要：先建被外键引用的表（users），再建引用它的表（chat_sessions），否则外键约束会报错

### 2. 迁移怎么知道连哪个库（backend/alembic/env.py）

`env.py` 是迁移的"运行环境"，核心两行：

```python
from app.core.config import get_settings
config.set_main_option("sqlalchemy.url", get_settings().database_url)
```

**数据库地址不是写死在 alembic.ini 里的，而是从应用配置读取**——这样开发（sqlite/postgres）、生产（postgres）自动用各自的环境变量，不会出现"迁移到了错误的库"。

`target_metadata = Base.metadata` 让 Alembic 知道"代码里定义的表结构"，`--autogenerate` 参数就是靠对比它和实际库的差异自动生成迁移。

### 3. 启动时自动迁移（backend/app/db/init_db.py）

```python
def _run_migrations() -> None:
    backend_dir = Path(__file__).resolve().parent.parent.parent
    try:
        from alembic import command
        from alembic.config import Config
        cfg = Config(str(backend_dir / "alembic.ini"))
        cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(cfg, "head")          # 迁移到最新版本
        logger.info("alembic upgrade head 完成")
    except Exception as exc:
        logger.warning("alembic 迁移不可用（%s），回退 create_all", exc)
        Base.metadata.create_all(bind=engine)  # 兜底
```

关键点：

- 容器启动时自动执行 `upgrade head`，**新服务器拉起来就是最新表结构**，不用手动跑命令。
- `try/except` 兜底：万一 alembic 没装（老环境），退回 `create_all` 保证能启动——但会打警告提醒你补装。

### 4. 版本记录表 `alembic_version`

第一次迁移后，数据库里会出现一张 `alembic_version` 表，只存一行：**当前迁移版本号**。

```text
alembic_version
┌───────────────┐
│ version_num   │
│ 0001_initial  │
└───────────────┘
```

下次 `upgrade head` 时，Alembic 对比这个版本号和迁移文件，只执行比它新的迁移——这就是"只升级、不重复执行"的机制。

## 关键命令逐条解释（怎么自己验证）

### 本机验证（需要先装 alembic）

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt        # 已含 alembic

# 1) 用 sqlite 临时库验证升级：建出全部 9 张表
$env:DATABASE_URL = 'sqlite:///./_mig_test.db'
python -m alembic upgrade head
# 期望输出：Running upgrade -> 0001_initial
# 然后确认表都在：python -c "import sqlite3; print([r[0] for r in sqlite3.connect('_mig_test.db').execute(\"select name from sqlite_master where type='table'\")])"
# 期望包含：users, ai_models, chat_sessions, chat_messages, documents, document_chunks, model_calls, refresh_tokens, document_tasks, alembic_version

# 2) 验证回滚：删除全部表
python -m alembic downgrade base
# 期望输出：Running downgrade 0001_initial -> 

# 3) 验证幂等：反复 upgrade/downgrade 不报错
Remove-Item _mig_test.db -ErrorAction SilentlyContinue
```

### 以后加新字段怎么做（重点，别跳过）

```powershell
# 1) 改 app/models/entities.py 里的模型（比如给 User 加 avatar 字段）
# 2) 自动生成迁移：alembic 对比代码和库的差异，生成迁移文件
python -m alembic revision --autogenerate -m "add user avatar"
# 3) 检查生成的 versions/xxxx_add_user_avatar.py 内容是否只含你要的改动
# 4) 执行迁移
python -m alembic upgrade head
```

**注意**：`--autogenerate` 生成的迁移**必须人工检查**——它可能把无关的差异（如默认值写法）也带进来，生产环境一定要 review 后再执行。

## 常见问题与避坑

1. **`create_all` 不会改表，Alembic 才会**：以后所有表结构变更必须走迁移，禁止再改 `create_all` 兜底来掩盖（兜底只用于"alembic 装不上"的开发场景）。
2. **生产库升级前先备份**：`alembic upgrade head` 之前先跑 `scripts/backup.sh`，万一迁移出错还能恢复（见 05 篇）。
3. **迁移文件一旦执行过就不要改**：版本文件是"历史记录"。要改逻辑就新写一个迁移，而不是回头改 `0001_initial`（会导致版本号与库状态对不上）。
4. **外键顺序**：建表先父后子，删表先子后父，手写迁移时最容易在这翻车。
5. **`--autogenerate` 结果必须 review**：它基于 metadata 对比，漏改模型或库里有脏数据都会生成错误迁移。
6. **多环境版本一致**：开发/测试/生产都执行 `upgrade head`，版本号必须一致，否则就是有人改了库没提交迁移。

## 小结

一句话记住：**Alembic = 数据库的 git，`upgrade head` 升级、`downgrade base` 回滚、`alembic_version` 表记版本；启动自动迁移，装不上时兜底 create_all；加字段必须走 autogenerate + review + upgrade。**
