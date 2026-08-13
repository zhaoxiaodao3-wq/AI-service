from datetime import datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import ok
from app.db.qdrant import check_qdrant
from app.db.session import check_database

# APIRouter 是 FastAPI 的路由分组；prefix="/api" 让本组所有路由都以 /api 开头
router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health():
    """健康检查接口：返回服务状态，并轻量探测 PostgreSQL 与 Qdrant。

    数据库/向量库探测失败时字段为 "error" 而不是抛异常，
    这样基础设施故障也能得到 200 响应，方便前端和后端定位是哪一端的问题。
    """
    settings = get_settings()
    return ok(
        {
            "service": settings.app_name,  # 服务名，便于多服务区分
            "time": datetime.now().astimezone().isoformat(),  # 带时区的当前时间
            "database": "ok" if check_database() else "error",
            "qdrant": "ok" if check_qdrant() else "error",
        }
    )
