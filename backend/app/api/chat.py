import json
import logging
import time

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from app.adapters.model_adapter import ModelError
from app.adapters.model_adapter import embed_texts
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.session import SessionLocal
from app.models.entities import User
from app.repositories import model_call_repo, vector_repo
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import stream_chat_events
from app.services import message_service, session_service

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger("app.chat")


def sse(data: dict) -> str:
    """把事件 dict 序列化成 SSE 文本：data: {...} 后跟空行。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(
    req: ChatStreamRequest, user: User = Depends(get_current_user)
):
    """SSE 流式对话接口。

    正常：逐段输出 delta，结束时输出 done；
    异常：输出 error 事件（含 code/message）而不是中断连接。
    """
    last_user_full = ""
    last_user = ""
    for msg in reversed(req.messages):
        if msg.get("role") == "user":
            last_user_full = str(msg.get("content", ""))
            last_user = last_user_full.replace("\n", " ").strip()[:80]
            break

    chat_session_id = req.session_id
    selected_model = req.model or get_settings().llm_model or get_settings().models[0]
    started_at = time.monotonic()
    if chat_session_id is not None:
        db = SessionLocal()
        try:
            session_service.get_session(db, chat_session_id, user.id)
            if last_user_full:
                message_service.add_message(db, chat_session_id, "user", last_user_full)
        finally:
            db.close()

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
        full_text = ""
        error_text = ""
        try:
            async for event in stream_chat_events(
                req.messages,
                req.model,
                use_rag=req.use_rag,
                session_id=req.session_id,
                user_id=user.id,
                use_tools=req.use_tools,
            ):
                kind = event.get("type", "?")
                counts[kind] = counts.get(kind, 0) + 1
                if kind == "delta":
                    chunk = event.get("content", "")
                    full_text += chunk
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
            error_text = f"[错误 {exc.code}] {exc.message}"
            logger.warning(
                "chat_stream model error code=%s message=%s",
                exc.code,
                exc.message,
            )
            yield sse({"type": "error", "code": exc.code, "message": exc.message})
        except Exception:
            # 兜底：不把堆栈暴露给前端
            counts["error"] += 1
            error_text = "[错误 unknown] 服务器内部错误，请稍后重试"
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
            if chat_session_id is not None:
                saved_text = full_text or error_text
                if saved_text:
                    db = SessionLocal()
                    try:
                        message_service.add_message(
                            db, chat_session_id, "assistant", saved_text
                        )
                        if (
                            last_user_full
                            and get_settings().memory_enabled
                        ):
                            try:
                                memory_text = (
                                    f"用户：{last_user_full}\nAI：{saved_text}"
                                )
                                memory_vector = (
                                    await embed_texts([memory_text])
                                )[0]
                                vector_repo.upsert_memory(
                                    user.id,
                                    chat_session_id,
                                    memory_text,
                                    memory_vector,
                                )
                            except Exception:
                                logger.warning(
                                    "memory save failed", exc_info=True
                                )
                        duration_ms = int((time.monotonic() - started_at) * 1000)
                        success = counts.get("error", 0) == 0
                        token_count = max(1, len(full_text) // 2) if full_text else None
                        model_call_repo.create_model_call(
                            db,
                            chat_session_id,
                            selected_model,
                            success,
                            token_count,
                            duration_ms,
                        )
                    finally:
                        db.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # 禁止中间层缓存流式响应
            "X-Accel-Buffering": "no",  # 关闭 Nginx 类代理缓冲，保证逐字输出
            "Connection": "keep-alive",
        },
    )
