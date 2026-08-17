import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
)

from app.core.config import get_settings


def _client() -> QdrantClient:
    return QdrantClient(url=get_settings().qdrant_url)


def _point_id(doc_id: int, index: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}-{index}"))


def upsert_document_chunks(
    doc_id: int, user_id: int, chunks: list[str], vectors: list[list[float]]
) -> None:
    """把切片原文、文档 ID、用户 ID 与向量一起写入 Qdrant。"""
    points = [
        PointStruct(
            id=_point_id(doc_id, index),
            vector=vector,
            payload={
                "doc_id": doc_id,
                "user_id": user_id,
                "text": chunk,
                "chunk_index": index,
            },
        )
        for index, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]
    _client().upsert(
        collection_name=get_settings().qdrant_collection_doc, points=points
    )


def search_documents(
    user_id: int,
    query_vector: list[float],
    top_k: int = 3,
    score_threshold: float = 0.35,
) -> list:
    """相似度检索：按用户过滤 + TopK + 相似度阈值。"""
    qfilter = Filter(
        must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    )
    return _client().search(
        collection_name=get_settings().qdrant_collection_doc,
        query_vector=query_vector,
        query_filter=qfilter,
        limit=top_k,
        score_threshold=score_threshold,
    )


def delete_document_vectors(doc_id: int) -> None:
    """按文档 ID 删除该文档全部向量。"""
    qfilter = Filter(
        must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
    )
    _client().delete(
        collection_name=get_settings().qdrant_collection_doc,
        points_selector=FilterSelector(filter=qfilter),
    )


def upsert_memory(
    user_id: int, session_id: int, text: str, vector: list[float]
) -> None:
    """写入一条长期记忆向量，payload 绑定用户与会话。"""
    point_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, f"memory-{session_id}-{text[:64]}")
    )
    _client().upsert(
        collection_name=get_settings().qdrant_collection_memory,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "user_id": user_id,
                    "session_id": session_id,
                    "text": text,
                    "type": "memory",
                },
            )
        ],
    )


def search_memories(
    user_id: int,
    query_vector: list[float],
    top_k: int = 3,
    score_threshold: float = 0.35,
    exclude_session_id: int | None = None,
) -> list:
    """检索历史记忆：按用户过滤，可排除当前会话避免重复注入。"""
    must = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    must_not = []
    if exclude_session_id is not None:
        must_not.append(
            FieldCondition(
                key="session_id", match=MatchValue(value=exclude_session_id)
            )
        )
    qfilter = Filter(must=must, must_not=must_not or None)
    return _client().search(
        collection_name=get_settings().qdrant_collection_memory,
        query_vector=query_vector,
        query_filter=qfilter,
        limit=top_k,
        score_threshold=score_threshold,
    )


def delete_session_memories(session_id: int) -> None:
    """删除某会话的全部记忆向量（删除会话时联动清理）。"""
    qfilter = Filter(
        must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
    )
    _client().delete(
        collection_name=get_settings().qdrant_collection_memory,
        points_selector=FilterSelector(filter=qfilter),
    )
