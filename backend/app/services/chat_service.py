from typing import AsyncIterator

from app.adapters.model_adapter import ChatRequest, stream_chat
from app.adapters.model_adapter import embed_texts
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories import user_repo, vector_repo
from app.services.document_service import build_rag_messages
from app.services.context_builder import truncate_messages


async def stream_chat_events(
    messages: list[dict], model: str | None, use_rag: bool = False
) -> AsyncIterator[dict]:
    """编排一次流式对话：截断上下文 → 调用适配层 → 产出 SSE 事件。"""
    s = get_settings()
    selected = model or s.llm_model or s.models[0]
    # 手动截断：超长上下文删除最早消息，防止模型窗口溢出
    safe_messages = truncate_messages(messages, s.max_context_tokens)
    if use_rag:
        question = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                question = str(m.get("content", ""))
                break
        if question:
            vectors = await embed_texts([question])
            with SessionLocal() as db:
                user_id = user_repo.get_default_user(db).id
            hits = vector_repo.search_documents(
                user_id,
                vectors[0],
                top_k=s.rag_top_k,
                score_threshold=s.rag_score_threshold,
            )
            if hits:
                safe_messages = build_rag_messages(safe_messages, hits)
    # 逐段取模型增量，包装成 SSE delta 事件
    async for delta in stream_chat(
        ChatRequest(model=selected, messages=safe_messages)
    ):
        yield {"type": "delta", "content": delta}
    # 流结束统一发 done；usage 阶段 5 再补真实统计
    yield {"type": "done", "usage": None}
