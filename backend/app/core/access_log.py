import json
import logging
import time

logger = logging.getLogger("app.access")


def _preview(text: str, limit: int = 80) -> str:
    """把多行文本压成单行并截断，避免日志被长内容刷屏。"""
    return text.replace("\n", " ").strip()[:limit]


def _body_summary(path: str, body: bytes) -> str:
    """生成请求体摘要：聊天接口输出结构，其他接口输出前 120 字。"""
    if not body:
        return "body_bytes=0"

    text = body.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
    except ValueError:
        return f"body_bytes={len(body)}"

    if not isinstance(data, dict):
        return f"body_bytes={len(body)}"

    if path == "/api/chat/stream":
        messages = data.get("messages") or []
        last_user = ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                last_user = _preview(str(msg.get("content", "")))
                break
        return (
            f"messages={len(messages)} model={data.get('model') or 'default'} "
            f"last_user='{last_user}'"
        )

    return f"json={text[:120]}"


class RequestLogMiddleware:
    """ASGI 中间件：记录每个 HTTP 请求的开始、请求体与结束状态。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        method = scope.get("method", "")
        path = scope.get("path", "")
        client = scope.get("client")
        client_ip = client[0] if client else "-"
        body = bytearray()
        body_logged = False
        response_status = 0
        response_bytes = 0

        async def receive_with_body():
            nonlocal body_logged
            message = await receive()
            if message["type"] == "http.request":
                body.extend(message.get("body", b""))
                if not message.get("more_body", False) and not body_logged:
                    body_logged = True
                    logger.info(
                        "request body method=%s path=%s %s",
                        method,
                        path,
                        _body_summary(path, bytes(body)),
                    )
            return message

        async def send_with_stats(message):
            nonlocal response_status, response_bytes
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_bytes += len(message.get("body", b""))
            await send(message)

        logger.info(
            "request start method=%s path=%s client=%s",
            method,
            path,
            client_ip,
        )
        try:
            await self.app(scope, receive_with_body, send_with_stats)
        except Exception:
            logger.exception("request error method=%s path=%s", method, path)
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "request end method=%s path=%s client=%s status=%s bytes=%s duration_ms=%.1f",
                method,
                path,
                client_ip,
                response_status,
                response_bytes,
                duration_ms,
            )
