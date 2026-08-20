"""LiteLLM 二次封装适配层。

职责：
- 统一模型调用的入参/出参（ChatRequest / ChatResponse）
- 支持官方直连与第三方中转双模式（只改 .env 即可切换）
- 把所有底层异常映射为统一 ModelError，方便接口层友好提示
"""

from dataclasses import dataclass
from typing import AsyncIterator

import httpx
import litellm

from app.core.config import get_settings
from app.services.local_embedding import embed_text as local_embed_text


class ModelError(Exception):
    """模型调用统一异常：code 给前端分类，message 给用户看。"""

    def __init__(self, code: str, message: str) -> None:
        self.code = code  # invalid_key / insufficient_quota / timeout / stream_broken / unknown
        self.message = message  # 用户可读中文提示
        super().__init__(message)


@dataclass
class ChatRequest:
    """统一聊天请求：无论底层哪个厂商，入参都收敛成这个结构。"""

    model: str  # 模型名，如 glm-4-flash / gpt-4o
    messages: list[dict]  # OpenAI 风格消息列表
    temperature: float = 0.7  # 随机性，越高越发散
    tools: list | None = None  # Function Calling 工具列表


@dataclass
class ChatResponse:
    """统一聊天响应：把不同厂商的返回收敛成统一结构。"""

    content: str  # 模型生成的完整文本
    usage: dict | None = None  # token 用量，阶段 5 统计用
    tool_calls: list | None = None  # 模型请求调用的工具


def _resolve_credentials(
    model_name: str | None = None,
) -> tuple[str, str | None] | None:
    """返回 (api_key, base_url)。

    优先级：
    1. ai_models 表里该模型的加密 Key（阶段 5 起支持每模型独立配置）
    2. .env 中转配置（开发调试）
    3. .env 官方直连
    都没有返回 None，由调用方抛 invalid_key。
    """
    if model_name:
        from app.core.security import decrypt_secret
        from app.db.session import SessionLocal
        from app.repositories import model_repo

        with SessionLocal() as db:
            model = model_repo.get_model_by_name(db, model_name)
            if model and model.api_key_encrypted:
                api_key = decrypt_secret(model.api_key_encrypted)
                if api_key:
                    return api_key, model.base_url or None

    s = get_settings()
    if s.llm_proxy_api_key and s.llm_proxy_base_url:
        return s.llm_proxy_api_key, s.llm_proxy_base_url
    if s.llm_api_key:
        return s.llm_api_key, s.llm_base_url or None
    return None


def _to_litellm_model(model: str, provider: str) -> str:
    """把配置里的干净模型名转成 LiteLLM 认识的模型名。

    智谱走 OpenAI 兼容协议，需要加 openai/ 前缀（openai/glm-4-flash），
    否则 LiteLLM 无法推断厂商；OpenAI/DeepSeek/Claude 这类
    已有默认推断的模型名保持不变。
    """
    if provider == "zhipu" and not model.startswith("openai/"):
        return f"openai/{model}"
    return model


def _map_error(exc: Exception) -> ModelError:
    """把 LiteLLM/底层异常映射成统一 ModelError，按特征文本分类。"""
    if isinstance(exc, httpx.TimeoutException):
        return ModelError("timeout", "模型响应超时，请重试")
    text = str(exc).lower()
    if "auth" in text or "401" in text or "invalid api key" in text:
        return ModelError("invalid_key", "API Key 无效，请检查配置")
    if "quota" in text or "429" in text or "insufficient" in text:
        return ModelError("insufficient_quota", "账户额度不足，请稍后重试")
    if "stream" in text or "connection" in text:
        return ModelError("stream_broken", "连接中断，请重新发送")
    return ModelError("unknown", f"模型调用失败：{exc}")


async def chat(request: ChatRequest) -> ChatResponse:
    """非流式对话：调用模型一次并返回完整内容。"""
    creds = _resolve_credentials(request.model)
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    litellm_model = _to_litellm_model(request.model, get_settings().llm_provider)
    try:
        resp = await litellm.acompletion(
            model=litellm_model,
            messages=request.messages,
            temperature=request.temperature,
            api_key=api_key,
            api_base=base_url,
            tools=request.tools,
        )
        # 统一取第一条 choice 的内容与工具调用
        message = resp.choices[0].message
        tool_calls = None
        if getattr(message, "tool_calls", None):
            tool_calls = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in message.tool_calls
            ]
        return ChatResponse(
            content=message.content,
            usage=dict(resp.usage) if resp.usage else None,
            tool_calls=tool_calls,
        )
    except Exception as exc:
        raise _map_error(exc) from exc


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    """流式对话：逐段产出文本增量，由上层转成 SSE delta 事件。"""
    creds = _resolve_credentials(request.model)
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    litellm_model = _to_litellm_model(request.model, get_settings().llm_provider)
    attempts = max(1, get_settings().llm_retry_count + 1)
    last_exc: Exception | None = None
    for _ in range(attempts):
        yielded = False
        try:
            # stream=True 时 acompletion 返回协程，await 后得到异步迭代器，逐块读取增量
            stream = await litellm.acompletion(
                model=litellm_model,
                messages=request.messages,
                temperature=request.temperature,
                api_key=api_key,
                api_base=base_url,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yielded = True
                    yield delta
            return
        except Exception as exc:
            last_exc = exc
            if yielded:
                raise _map_error(exc) from exc
    if last_exc is not None:
        raise _map_error(last_exc) from last_exc


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量文本向量化：调用 Embedding 模型，返回每个文本的向量。"""
    s = get_settings()
    if s.embedding_mode == "local":
        return [local_embed_text(t) for t in texts]
    api_key = s.embedding_api_key or s.llm_api_key or s.llm_proxy_api_key
    base_url = s.embedding_base_url or s.llm_base_url or None
    if not api_key:
        raise ModelError("invalid_key", "未配置 Embedding API Key")
    model = _to_litellm_model(s.embedding_model, s.llm_provider or "openai")
    try:
        resp = await litellm.aembedding(
            model=model,
            input=texts,
            api_key=api_key,
            api_base=base_url,
        )
        return [
            item["embedding"] if isinstance(item, dict) else item.embedding
            for item in resp.data
        ]
    except Exception as exc:
        raise _map_error(exc) from exc


async def rerank(
    query: str, documents: list[str], model: str | None = None
) -> list[float] | None:
    """Rerank 精排：调用 SiliconFlow /v1/rerank，失败返回 None 回退 RRF。"""
    s = get_settings()
    api_key = s.rerank_api_key or s.embedding_api_key or s.llm_api_key or s.llm_proxy_api_key
    base = s.rerank_base_url or s.embedding_base_url or s.llm_base_url
    if not api_key or not base:
        return None
    model = model or s.rerank_model
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                base.rstrip("/") + "/rerank",
                headers={"Authorization": "Bearer " + api_key},
                json={"model": model, "query": query, "documents": documents},
            )
            resp.raise_for_status()
            data = resp.json()
        results = data.get("results") or []
        ordered: list[float] = [0.0] * len(documents)
        for item in results:
            index = item.get("index")
            if index is not None and 0 <= index < len(documents):
                ordered[index] = item.get("relevance_score", 0.0)
        return ordered
    except Exception:
        return None
