from sqlalchemy.orm import Session

from app.models.entities import Document


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
