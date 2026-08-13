from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "ok") -> JSONResponse:
    """构造成功响应，统一格式 {code:0, message, data}。

    前端只认这一种结构，方便统一解析；code=0 表示成功。
    """
    return JSONResponse({"code": 0, "message": message, "data": data})


def fail(
    code: int,
    message: str,
    data: Any = None,
    http_status: int = 400,
) -> JSONResponse:
    """构造失败响应，统一格式 {code, message, data}。

    code 是业务错误码（非 0），http_status 是 HTTP 状态码；
    两者分离让前端既能按 HTTP 判断，也能按业务码处理。
    """
    return JSONResponse(
        {"code": code, "message": message, "data": data},
        status_code=http_status,
    )
