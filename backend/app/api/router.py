from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.models import router as models_router

# 汇总所有业务路由：后续新增模块时在这里 include 即可，main.py 不用改
api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(models_router)
