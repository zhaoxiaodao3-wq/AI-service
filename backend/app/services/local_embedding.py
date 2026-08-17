import hashlib
import math

from app.core.config import get_settings


def embed_text(text: str, dimensions: int | None = None) -> list[float]:
    """开发期本地向量：字符二元组哈希到固定维度，归一化后用于 RAG 演示。

    生产环境应使用真实 Embedding 模型（embedding_mode=api）。
    """
    dims = dimensions or get_settings().embedding_dimensions
    vector = [0.0] * dims
    lowered = text.lower().strip()
    for i in range(len(lowered) - 1):
        gram = lowered[i : i + 2]
        index = int(hashlib.md5(gram.encode("utf-8")).hexdigest()[:8], 16) % dims
        vector[index] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]
