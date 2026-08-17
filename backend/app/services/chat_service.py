import json
from typing import AsyncIterator

from app.adapters.model_adapter import ChatRequest, chat, stream_chat
from app.adapters.model_adapter import embed_texts
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories import user_repo, vector_repo
from app.services.document_service import build_rag_messages
from app.services.context_builder import truncate_messages
from app.tools.registry import execute_tool, list_tools


async def stream_chat_events(
    messages: list[dict],
    model: str | None,
    use_rag: bool = False,
    session_id: int | None = None,
    user_id: int | None = None,
    use_tools: bool = False,
) -> AsyncIterator[dict]:
    """编排一次流式对话：截断上下文 → 调用适配层 → 产出 SSE 事件。"""
    s = get_settings()
    selected = model or s.llm_model or s.models[0]
    # 手动截断：超长上下文删除最早消息，防止模型窗口溢出
    safe_messages = truncate_messages(messages, s.max_context_tokens)
    question = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            question = str(m.get("content", ""))
            break

    hits = []
    memories = []
    if (use_rag or session_id is not None) and question:
        vectors = await embed_texts([question])
        if user_id is None:
            with SessionLocal() as db:
                user_id = user_repo.get_default_user(db).id
        if use_rag:
            hits = vector_repo.search_documents(
                user_id,
                vectors[0],
                top_k=s.rag_top_k,
                score_threshold=s.rag_score_threshold,
            )
        if session_id is not None and s.memory_enabled:
            memories = vector_repo.search_memories(
                user_id,
                vectors[0],
                top_k=s.memory_top_k,
                score_threshold=s.memory_score_threshold,
                exclude_session_id=session_id,
            )
    if hits or memories:
        safe_messages = build_rag_messages(
            safe_messages, hits=hits or None, memories=memories or None
        )

    if use_tools and s.tools_enabled:
        current = safe_messages
        for _ in range(s.max_tool_rounds):
            resp = await chat(
                ChatRequest(
                    model=selected,
                    messages=current,
                    tools=list_tools(),
                )
            )
            if not resp.tool_calls:
                if resp.content:
                    yield {"type": "delta", "content": resp.content}
                    yield {"type": "done", "usage": resp.usage}
                    return
                break
            current.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc.get("arguments", ""),
                            },
                        }
                        for tc in resp.tool_calls
                    ],
                }
            )
            for tc in resp.tool_calls:
                yield {
                    "type": "tool_start",
                    "tool": tc["name"],
                    "arguments": tc.get("arguments", ""),
                }
                try:
                    arguments = json.loads(tc.get("arguments") or "{}")
                except json.JSONDecodeError:
                    arguments = {}
                result = await execute_tool(tc["name"], arguments, user_id)
                yield {"type": "tool_done", "tool": tc["name"], "result": result[:200]}
                current.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    }
                )
        safe_messages = current

    # 逐段取模型增量，包装成 SSE delta 事件
    async for delta in stream_chat(
        ChatRequest(model=selected, messages=safe_messages)
    ):
        yield {"type": "delta", "content": delta}
    # 流结束统一发 done；usage 阶段 5 再补真实统计
    yield {"type": "done", "usage": None}
