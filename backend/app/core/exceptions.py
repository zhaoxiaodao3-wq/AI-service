from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .response import fail


class AppError(Exception):
    def __init__(self, code: int = 400, message: str = "请求错误") -> None:
        self.code = code
        self.message = message


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return fail(exc.code, exc.message)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return fail(500, "服务器内部错误", http_status=500)
