from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    """流式对话请求体：历史消息 + 可选模型名。"""

    messages: list[dict] = Field(
        ..., min_length=1, description="消息列表，含历史与最新用户消息"
    )
    model: str | None = Field(
        None, description="模型名；缺省时使用 .env 配置的默认模型"
    )
    session_id: int | None = Field(
        None, description="会话 ID；提供时后端自动保存本轮消息"
    )
