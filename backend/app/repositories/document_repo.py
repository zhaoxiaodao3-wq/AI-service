from sqlalchemy.orm import Session

from app.models.entities import Document, DocumentChunk


def create_document(
    db: Session,
    user_id: int,
    filename: str,
    file_type: str,
    file_size: int,
    chunk_count: int,
) -> Document:
    document = Document(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        chunk_count=chunk_count,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, user_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter_by(user_id=user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, document_id: int, user_id: int) -> Document | None:
    return db.query(Document).filter_by(id=document_id, user_id=user_id).first()


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()


def add_chunks(db: Session, document_id: int, chunks: list[str]) -> None:
    """把切片原文写入 PG，供关键词检索。"""
    for index, content in enumerate(chunks):
        db.add(
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
            )
        )
    db.commit()


def get_filenames_by_ids(db: Session, document_ids: list[int]) -> dict[int, str]:
    if not document_ids:
        return {}
    rows = (
        db.query(Document.id, Document.filename)
        .filter(Document.id.in_(document_ids))
        .all()
    )
    return {row[0]: row[1] for row in rows}
