"""LiteLLM 二次封装占位层。

阶段 1 将在此实现统一入参/出参、官方 Key 与中转 Key 切换、流式接口。
本阶段只定义协议，不调用任何真实模型。
"""

from dataclasses import dataclass
from typing import AsyncIterator


class ModelError(Exception):
    """模型调用异常的统一类型，阶段 1 由适配层抛出。"""


@dataclass
class ChatRequest:
    """统一聊天请求：无论底层是哪个厂商，入参都收敛成这个结构。"""

    model: str  # 模型名，如 gpt-4o / deepseek-chat
    messages: list[dict]  # OpenAI 风格消息列表 [{"role": "user", "content": "..."}]
    temperature: float = 0.7  # 随机性：越高回答越发散


@dataclass
class ChatResponse:
    """统一聊天响应：把不同厂商的返回收敛成统一结构。"""

    content: str  # 模型生成的文本
    usage: dict | None = None  # token 用量信息，阶段 5 统计用


async def chat(request: ChatRequest) -> ChatResponse:
    """非流式对话入口，阶段 1 实现真实调用。"""
    raise NotImplementedError("阶段 1 实现")


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    """流式对话入口，阶段 1 实现 SSE 分片输出。"""
    raise NotImplementedError("阶段 1 实现")
