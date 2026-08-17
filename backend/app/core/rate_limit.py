import asyncio
import time
from collections import defaultdict

from fastapi.responses import JSONResponse


class RateLimitMiddleware:
    """单机滑动窗口限流：只限制 chat 流式接口，避免被刷。"""

    def __init__(self, app, limit: int = 30, window: int = 60):
        self.app = app
        self.limit = limit
        self.window = window
        self.hits: dict[str, list[float]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") != "/api/chat/stream":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        key = client[0] if client else "unknown"
        now = time.monotonic()
        async with self.lock:
            cutoff = now - self.window
            self.hits[key] = [t for t in self.hits[key] if t > cutoff]
            if len(self.hits[key]) >= self.limit:
                response = JSONResponse(
                    {"code": 429, "message": "请求过于频繁，请稍后再试"},
                    status_code=429,
                )
                await response(scope, receive, send)
                return
            self.hits[key].append(now)

        await self.app(scope, receive, send)
