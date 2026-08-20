from sqlalchemy.orm import Session

from app.models.entities import Document, DocumentChunk


def search_keyword(
    db: Session, user_id: int, query: str, limit: int = 8
) -> list[DocumentChunk]:
    """关键词检索：按用户过滤 + 内容 ILIKE，演示 BM25 之外的简单方案。"""
    pattern = f"%{query}%"
    return (
        db.query(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(
            Document.user_id == user_id,
            DocumentChunk.content.ilike(pattern),
        )
        .order_by(DocumentChunk.id.asc())
        .limit(limit)
        .all()
    )
