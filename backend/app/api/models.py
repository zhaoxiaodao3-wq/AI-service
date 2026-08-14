from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.response import ok
from app.db.session import get_db
from app.services.model_service import list_models

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
def list_models_endpoint(db: Session = Depends(get_db)):
    """返回当前模式、可用模型清单与默认模型，供前端下拉渲染。

    mode：proxy 表示走了中转配置；official 表示官方直连。
    默认模型取 LLM_MODEL，未配置则取模型清单第一个。
    """
    s = get_settings()
    mode = "proxy" if (s.llm_proxy_api_key and s.llm_proxy_base_url) else "official"
    models, default_model = list_models(db)
    return ok(
        {
            "mode": mode,
            "models": models,
            "default_model": default_model,
        }
    )
