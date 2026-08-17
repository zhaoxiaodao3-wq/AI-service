from typing import Any, Awaitable, Callable


class Tool:
    """工具定义：模型看到的是 OpenAI 格式，执行走 handler。"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[[dict, int | None], Awaitable[str]],
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_openai(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
