from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """新建会话请求：标题与模型可选。"""

    title: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=128)


class SessionRename(BaseModel):
    """重命名会话请求。"""

    title: str = Field(..., min_length=1, max_length=255)


class SessionOut(BaseModel):
    """会话响应。"""

    id: int
    title: str
    model: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    """消息响应。"""

    id: int
    role: str
    content: str
    token_count: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
