from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .response import fail


class AppError(Exception):
    """业务异常基类：业务代码主动抛出的错误统一用它。

    相比直接返回错误响应，抛异常能让服务层代码更简洁，
    所有错误集中在这里处理。
    """

    def __init__(self, code: int = 400, message: str = "请求错误") -> None:
        self.code = code  # 业务错误码
        self.message = message  # 给用户看的错误信息


def register_exception_handlers(app: FastAPI) -> None:
    """向 FastAPI 注册全局异常处理器，统一错误响应格式。"""

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        # 捕获业务主动抛出的 AppError，按其中携带的 code/message 返回
        return fail(exc.code, exc.message)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        # 兜底：未预期的异常返回 500，避免把堆栈信息直接暴露给前端
        return fail(500, "服务器内部错误", http_status=500)
