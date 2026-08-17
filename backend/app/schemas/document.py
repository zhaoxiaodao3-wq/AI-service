from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    """文档元信息响应。"""

    id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
