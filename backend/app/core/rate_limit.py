import asyncio
import time
import uuid
from collections import defaultdict

from fastapi.responses import JSONResponse
from redis import Redis

from app.core.config import get_settings
from app.core.security import decode_access_token


class RateLimitMiddleware:
    """分布式滑动窗口限流：优先 Redis，异常时回退单机内存。"""

    def __init__(
        self,
        app,
        limit: int = 30,
        window: int = 60,
        user_limit: int = 60,
    ):
        self.app = app
        self.limit = limit
        self.window = window
        self.user_limit = user_limit
        self.hits: dict[str, list[float]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") != "/api/chat/stream":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        key = client[0] if client else "unknown"
        limit = self.limit
        for header in scope.get("headers", []):
            if header[0] == b"authorization" and header[1].startswith(b"Bearer "):
                payload = decode_access_token(header[1][7:].decode("utf-8"))
                if payload:
                    key = f"user:{payload.get('sub')}"
                    limit = self.user_limit
                break

        allowed = await self._check(key, limit, self.window)
        if not allowed:
            response = JSONResponse(
                {"code": 429, "message": "请求过于频繁，请稍后再试"},
                status_code=429,
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _check(self, key: str, limit: int, window: int) -> bool:
        try:
            client = Redis.from_url(get_settings().redis_url, decode_responses=True)
            now = time.time()
            member = str(uuid.uuid4())
            pipeline = client.pipeline()
            pipeline.zadd(key, {member: now})
            pipeline.zremrangebyscore(key, 0, now - window)
            pipeline.zcard(key)
            pipeline.expire(key, window * 2)
            _added, _removed, count, _expired = pipeline.execute()
            client.close()
            return int(count) <= limit
        except Exception:
            async with self.lock:
                cutoff = time.monotonic() - window
                self.hits[key] = [t for t in self.hits[key] if t > cutoff]
                if len(self.hits[key]) >= limit:
                    return False
                self.hits[key].append(time.monotonic())
                return True
