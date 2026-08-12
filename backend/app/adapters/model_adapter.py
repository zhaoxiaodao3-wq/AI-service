"""LiteLLM 二次封装占位层。

阶段 1 将在此实现统一入参/出参、官方 Key 与中转 Key 切换、流式接口。
本阶段只定义协议，不调用任何真实模型。
"""

from dataclasses import dataclass
from typing import AsyncIterator


class ModelError(Exception):
    """模型调用异常的统一类型。"""


@dataclass
class ChatRequest:
    model: str
    messages: list[dict]
    temperature: float = 0.7


@dataclass
class ChatResponse:
    content: str
    usage: dict | None = None


async def chat(request: ChatRequest) -> ChatResponse:
    raise NotImplementedError("阶段 1 实现")


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    raise NotImplementedError("阶段 1 实现")
