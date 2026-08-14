from app.core.config import get_settings
from app.repositories import model_repo


def list_models(db) -> tuple[list[str], str]:
    """从数据库读取启用模型；空表时回退静态配置。"""
    models = model_repo.list_enabled_models(db)
    if not models:
        s = get_settings()
        return s.models, s.llm_model or s.models[0]
    names = [m.name for m in models]
    s = get_settings()
    default = s.llm_model if s.llm_model in names else names[0]
    return names, default
