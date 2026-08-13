from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

# 应用启动时读取配置并创建数据库连接引擎（连接池）
settings = get_settings()

# create_engine 创建连接池；pool_pre_ping 在每次取连接前先做一次连通探测，
# 避免拿到已被数据库断开的旧连接导致请求报错
engine = create_engine(settings.database_url, pool_pre_ping=True)

# sessionmaker 是产生数据库会话的工厂；autoflush=False 避免查询前自动刷写，
# expire_on_commit=False 保证提交后对象属性仍可读取
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：为每个请求提供一个数据库会话，请求结束自动关闭。

    yield 之前的代码在请求开始时执行，yield 之后的 finally 在请求结束时执行，
    这样每个请求独占一个会话，用完必关，不会泄漏连接。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    """探测数据库是否可连接：执行 SELECT 1，成功返回 True。

    健康检查接口用它判断 PostgreSQL 状态；任何连接异常都被捕获并返回 False，
    不让数据库故障拖垮整个接口。
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
