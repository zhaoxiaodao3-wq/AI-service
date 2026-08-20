from sqlalchemy.orm import Session

from app.models.entities import DocumentTask


def create_task(db: Session, document_id: int, file_path: str) -> DocumentTask:
    task = DocumentTask(document_id=document_id, file_path=file_path)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> DocumentTask | None:
    return db.query(DocumentTask).filter_by(id=task_id).first()


def latest_by_document(db: Session, document_id: int) -> DocumentTask | None:
    return (
        db.query(DocumentTask)
        .filter_by(document_id=document_id)
        .order_by(DocumentTask.id.desc())
        .first()
    )


def update_status(
    db: Session, task: DocumentTask, status: str, error: str | None = None
) -> DocumentTask:
    task.status = status
    task.error = error
    db.commit()
    db.refresh(task)
    return task
