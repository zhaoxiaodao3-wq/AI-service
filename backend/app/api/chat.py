import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.adapters.model_adapter import ModelError
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import stream_chat_events

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger("app.chat")


def sse(data: dict) -> str:
    """把事件 dict 序列化成 SSE 文本：data: {...} 后跟空行。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    """SSE 流式对话接口。

    正常：逐段输出 delta，结束时输出 done；
    异常：输出 error 事件（含 code/message）而不是中断连接。
    """
    last_user = ""
    for msg in reversed(req.messages):
        if msg.get("role") == "user":
            last_user = str(msg.get("content", "")).replace("\n", " ").strip()[:80]
            break
    logger.info(
        "chat_stream start messages=%d model=%s preview='%s'",
        len(req.messages),
        req.model or "default",
        last_user,
    )

    async def event_stream():
        counts = {"delta": 0, "done": 0, "error": 0}
        chars = 0
        preview = ""
        try:
            async for event in stream_chat_events(req.messages, req.model):
                kind = event.get("type", "?")
                counts[kind] = counts.get(kind, 0) + 1
                if kind == "delta":
                    chunk = event.get("content", "")
                    chars += len(chunk)
                    preview = (preview + chunk)[:80]
                    logger.info(
                        "chat_stream delta chunk='%s' chunk_chars=%d total_chars=%d",
                        chunk.replace("\n", " ")[:80],
                        len(chunk),
                        chars,
                    )
                yield sse(event)
        except ModelError as exc:
            # 模型侧错误：转成 SSE error 事件，前端按 code 提示
            counts["error"] += 1
            logger.warning(
                "chat_stream model error code=%s message=%s",
                exc.code,
                exc.message,
            )
            yield sse({"type": "error", "code": exc.code, "message": exc.message})
        except Exception:
            # 兜底：不把堆栈暴露给前端
            counts["error"] += 1
            logger.exception("chat_stream unexpected error")
            yield sse(
                {"type": "error", "code": "unknown", "message": "服务器内部错误，请稍后重试"}
            )
        finally:
            logger.info(
                "chat_stream finish events=%s chars=%d preview='%s'",
                counts,
                chars,
                preview,
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # 禁止中间层缓存流式响应
            "X-Accel-Buffering": "no",  # 关闭 Nginx 类代理缓冲，保证逐字输出
            "Connection": "keep-alive",
        },
    )
