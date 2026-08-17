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
