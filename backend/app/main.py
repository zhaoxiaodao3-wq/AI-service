from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.access_log import RequestLogMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.rate_limit import RateLimitMiddleware
from app.core.telemetry import setup_telemetry
from app.db.init_db import init_db
from app.db.qdrant import ensure_collections

# 启动前先初始化日志，保证后续所有日志都走统一格式
setup_logging()
# 启动前初始化 OpenTelemetry（失败静默降级，不影响启动）
setup_telemetry()
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用启动时初始化数据库表与种子数据，幂等可重复执行。"""
    init_db()
    ensure_collections()
    yield


# 创建 FastAPI 应用实例，title 会显示在 /docs 文档页
app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS 中间件：允许本地前端（5173）跨域访问后端接口。
# 本阶段前端走 Vite 代理，通常不触发跨域，这里预留直连场景。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求/响应日志中间件：所有 HTTP 请求都会留下开始、请求体、结束三行日志
app.add_middleware(RequestLogMiddleware)

# 聊天接口限流：按客户端 IP 滑动窗口，防止刷接口
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.rate_limit_per_minute,
    user_limit=settings.rate_limit_user_per_minute,
)

# 注册统一异常处理（AppError 与兜底 500）
register_exception_handlers(app)

# 挂载所有业务路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径：简单返回一句提示，方便浏览器直接确认服务已启动。"""
    return {"message": "aigc-backend is running"}
