import logging
from pathlib import Path

from app.core.config import get_settings
from app.core.security import encrypt_secret
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import AiModel, User

logger = logging.getLogger("app.db")


def _guess_provider(name: str) -> str:
    """根据模型名粗判厂商，阶段 5 会改为完整配置化。"""
    if name.startswith("glm"):
        return "zhipu"
    if name.startswith("claude"):
        return "anthropic"
    if name.startswith("deepseek"):
        return "deepseek"
    return "openai"


def _run_migrations() -> None:
    """表结构迁移：优先 Alembic（upgrade head），不可用时回退 create_all。

    阶段 12 起容器内通过 requirements.txt 安装 alembic，启动即执行迁移；
    本地/旧环境未装 alembic 时回退建表并打警告，保证开发不被阻断。
    """
    backend_dir = Path(__file__).resolve().parent.parent.parent
    try:
        from alembic import command
        from alembic.config import Config

        cfg = Config(str(backend_dir / "alembic.ini"))
        cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(cfg, "head")
        logger.info("alembic upgrade head 完成，数据库结构已对齐")
    except Exception as exc:
        logger.warning(
            "alembic 迁移不可用（%s），回退 create_all 建表", exc
        )
        Base.metadata.create_all(bind=engine)


def init_db() -> None:
    """迁移建表并写入种子数据：默认用户 + 模型配置（API Key 加密）。"""
    _run_migrations()
    s = get_settings()

    with SessionLocal() as db:
        # 默认本地用户：阶段 2 不做登录，所有会话先挂在 id=1 下
        if db.query(User).filter_by(username="local").first() is None:
            db.add(User(username="local", password_hash=""))

        # 模型种子：从静态配置导入一次，之后以数据库为准
        existing = {m.name for m in db.query(AiModel).all()}
        api_key = s.llm_api_key or s.llm_proxy_api_key
        for weight, name in enumerate(s.models):
            if name not in existing:
                db.add(
                    AiModel(
                        name=name,
                        provider=_guess_provider(name),
                        base_url=s.llm_base_url or "",
                        api_key_encrypted=encrypt_secret(api_key),
                        enabled=True,
                        weight=weight,
                    )
                )
        db.commit()
