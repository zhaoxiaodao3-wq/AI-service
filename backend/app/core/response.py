from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "ok") -> JSONResponse:
    return JSONResponse({"code": 0, "message": message, "data": data})


def fail(
    code: int,
    message: str,
    data: Any = None,
    http_status: int = 400,
) -> JSONResponse:
    return JSONResponse(
        {"code": code, "message": message, "data": data},
        status_code=http_status,
    )
