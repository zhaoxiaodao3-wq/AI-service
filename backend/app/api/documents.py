from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.adapters.model_adapter import embed_texts
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.response import ok
from app.db.session import get_db
from app.models.entities import User
from app.repositories import document_repo, vector_repo
from app.schemas.document import DocumentOut
from app.services import document_service
from app.services.chunker import split_text

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _payload(document) -> dict:
    return DocumentOut.model_validate(document).model_dump(mode="json")


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传文档：解析 → 切片 → 向量化 → PG 元信息 → Qdrant 入库。"""
    content = await file.read()
    filename = file.filename or "unnamed"
    if not content:
        raise AppError(400, "文件内容为空")
    if len(content) > document_service.MAX_FILE_SIZE:
        raise AppError(400, "文件不能超过 5MB")

    text = document_service.parse_file(content, filename)
    if not text.strip():
        raise AppError(400, "未能从文档中提取到文本")

    s = get_settings()
    chunks = split_text(text, s.chunk_size, s.chunk_overlap)
    if not chunks:
        raise AppError(400, "文档切片为空")

    vectors = await embed_texts(chunks)
    ext = filename.rsplit(".", 1)[-1].lower()
    document = document_repo.create_document(
        db,
        user.id,
        filename,
        ext,
        len(content),
        len(chunks),
    )
    vector_repo.upsert_document_chunks(document.id, user.id, chunks, vectors)
    return ok({"document": _payload(document)})


@router.get("")
def list_documents(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """列出当前用户的已上传文档。"""
    documents = document_repo.list_documents(db, user.id)
    return ok({"documents": [_payload(d) for d in documents]})


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
