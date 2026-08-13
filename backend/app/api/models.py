from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import ok

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
async def list_models():
    """返回当前模式、可用模型清单与默认模型，供前端下拉渲染。

    mode：proxy 表示走了中转配置；official 表示官方直连。
    默认模型取 LLM_MODEL，未配置则取模型清单第一个。
    """
    s = get_settings()
    mode = "proxy" if (s.llm_proxy_api_key and s.llm_proxy_base_url) else "official"
    return ok(
        {
            "mode": mode,
            "models": s.models,
            "default_model": s.llm_model or s.models[0],
        }
    )
