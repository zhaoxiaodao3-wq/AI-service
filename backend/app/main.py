from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.access_log import RequestLogMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

# 启动前先初始化日志，保证后续所有日志都走统一格式
setup_logging()
settings = get_settings()

# 创建 FastAPI 应用实例，title 会显示在 /docs 文档页
app = FastAPI(title=settings.app_name)

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

# 注册统一异常处理（AppError 与兜底 500）
register_exception_handlers(app)

# 挂载所有业务路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径：简单返回一句提示，方便浏览器直接确认服务已启动。"""
    return {"message": "aigc-backend is running"}
