from typing import AsyncIterator

from app.adapters.model_adapter import ChatRequest, stream_chat
from app.core.config import get_settings
from app.services.context_builder import truncate_messages


async def stream_chat_events(
    messages: list[dict], model: str | None
) -> AsyncIterator[dict]:
    """编排一次流式对话：截断上下文 → 调用适配层 → 产出 SSE 事件。"""
    s = get_settings()
    selected = model or s.llm_model or s.models[0]
    # 手动截断：超长上下文删除最早消息，防止模型窗口溢出
    safe_messages = truncate_messages(messages, s.max_context_tokens)
    # 逐段取模型增量，包装成 SSE delta 事件
    async for delta in stream_chat(
        ChatRequest(model=selected, messages=safe_messages)
    ):
        yield {"type": "delta", "content": delta}
    # 流结束统一发 done；usage 阶段 5 再补真实统计
    yield {"type": "done", "usage": None}
