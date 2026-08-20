import pathlib
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.adapters.model_adapter import embed_texts
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.response import ok
from app.db.session import get_db
from app.models.entities import User
from app.repositories import document_repo, document_task_repo, vector_repo
from app.schemas.document import DocumentOut
from app.services import document_service
from app.services.chunker import split_text
from app.services.task_queue import enqueue_document_task

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _payload(document) -> dict:
    return DocumentOut.model_validate(document).model_dump(mode="json")


def _task_payload(task) -> dict:
    if task is None:
        return None
    return {
        "id": task.id,
        "status": task.status,
        "error": task.error,
    }


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传文档：保存临时文件并异步入队处理。"""
    content = await file.read()
    filename = file.filename or "unnamed"
    if not content:
        raise AppError(400, "文件内容为空")
    if len(content) > document_service.MAX_FILE_SIZE:
        raise AppError(400, "文件不能超过 5MB")

    ext = filename.rsplit(".", 1)[-1].lower()
    document = document_repo.create_document(
        db,
        user.id,
        filename,
        ext,
        len(content),
        0,
    )
    upload_dir = pathlib.Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4().hex}.{ext}"
    file_path.write_bytes(content)
    task = document_task_repo.create_task(db, document.id, str(file_path))
    enqueue_document_task(task.id)
    return ok({"document": _payload(document), "task": _task_payload(task)})


@router.get("")
def list_documents(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """列出当前用户的已上传文档。"""
    documents = document_repo.list_documents(db, user.id)
    items = []
    for doc in documents:
        item = _payload(doc)
        task = document_task_repo.latest_by_document(db, doc.id)
        item["task_status"] = _task_payload(task)
        items.append(item)
    return ok({"documents": items})


@router.get("/{document_id}/task")
def get_task_status(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询文档异步任务状态。"""
    document_service.get_document(db, document_id, user.id)
    task = document_task_repo.latest_by_document(db, document_id)
    return ok({"task": _task_payload(task)})


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除文档元信息与 Qdrant 向量。"""
    document = document_service.get_document(db, document_id, user.id)
    vector_repo.delete_document_vectors(document.id)
    document_repo.delete_document(db, document)
    return ok({"deleted": True})
