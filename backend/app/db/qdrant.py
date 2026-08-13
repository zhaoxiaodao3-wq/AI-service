from qdrant_client import QdrantClient

from app.core.config import get_settings

settings = get_settings()

DISTANCE = "Cosine"
VECTOR_SIZE = 1536  # 阶段 3/4 按实际 Embedding 模型调整


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collections() -> list[str]:
    client = get_qdrant_client()
    names = [settings.qdrant_collection_doc, settings.qdrant_collection_memory]
    existing = {c.name for c in client.get_collections().collections}
    for name in names:
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config={
                    "size": VECTOR_SIZE,
                    "distance": DISTANCE,
                },
            )
    return names


def check_qdrant() -> bool:
    try:
        get_qdrant_client().get_collections()
        return True
    except Exception:
        return False
