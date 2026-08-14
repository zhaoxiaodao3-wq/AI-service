from app.core.config import get_settings
from app.core.security import encrypt_secret
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import AiModel, User


def _guess_provider(name: str) -> str:
    """根据模型名粗判厂商，阶段 5 会改为完整配置化。"""
    if name.startswith("glm"):
        return "zhipu"
    if name.startswith("claude"):
        return "anthropic"
    if name.startswith("deepseek"):
        return "deepseek"
    return "openai"


def init_db() -> None:
    """建表并写入种子数据：默认用户 + 模型配置（API Key 加密）。"""
    Base.metadata.create_all(bind=engine)
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
