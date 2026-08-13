import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.adapters.model_adapter import ModelError
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import stream_chat_events

router = APIRouter(prefix="/api", tags=["chat"])


def sse(data: dict) -> str:
    """把事件 dict 序列化成 SSE 文本：data: {...} 后跟空行。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    """SSE 流式对话接口。

    正常：逐段输出 delta，结束时输出 done；
    异常：输出 error 事件（含 code/message）而不是中断连接。
    """

    async def event_stream():
        try:
            async for event in stream_chat_events(req.messages, req.model):
                yield sse(event)
        except ModelError as exc:
            # 模型侧错误：转成 SSE error 事件，前端按 code 提示
            yield sse({"type": "error", "code": exc.code, "message": exc.message})
        except Exception:
            # 兜底：不把堆栈暴露给前端
            yield sse(
                {"type": "error", "code": "unknown", "message": "服务器内部错误，请稍后重试"}
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
