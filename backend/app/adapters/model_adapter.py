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


@dataclass
class ChatResponse:
    """统一聊天响应：把不同厂商的返回收敛成统一结构。"""

    content: str  # 模型生成的完整文本
    usage: dict | None = None  # token 用量，阶段 5 统计用


def _resolve_credentials() -> tuple[str, str | None] | None:
    """返回 (api_key, base_url)。

    优先级：中转配置非空走中转（开发调试），否则走官方直连；
    两者都没有返回 None，由调用方抛 invalid_key。
    这样「官方/中转」切换只改 .env，不改代码。
    """
    s = get_settings()
    if s.llm_proxy_api_key and s.llm_proxy_base_url:
        return s.llm_proxy_api_key, s.llm_proxy_base_url
    if s.llm_api_key:
        return s.llm_api_key, s.llm_base_url or None
    return None


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
    creds = _resolve_credentials()
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    try:
        resp = await litellm.acompletion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            api_key=api_key,
            api_base=base_url,
        )
        # 统一取第一条 choice 的内容
        content = resp.choices[0].message.content
        return ChatResponse(
            content=content,
            usage=dict(resp.usage) if resp.usage else None,
        )
    except Exception as exc:
        raise _map_error(exc) from exc


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    """流式对话：逐段产出文本增量，由上层转成 SSE delta 事件。"""
    creds = _resolve_credentials()
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    try:
        # stream=True 时 acompletion 直接返回异步迭代器（无需 await），逐块读取增量
        stream = litellm.acompletion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            api_key=api_key,
            api_base=base_url,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        raise _map_error(exc) from exc
