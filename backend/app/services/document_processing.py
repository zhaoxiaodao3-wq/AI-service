import asyncio
import os

from app.adapters.model_adapter import embed_texts
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.entities import Document
from app.repositories import document_repo, document_task_repo, vector_repo
from app.services.chunker import split_text
from app.services.document_service import parse_file
from app.services.security_service import is_prompt_injection


def process_document_task(task_id: int) -> None:
    """RQ worker 入口：解析 → 切片 → 向量化 → 入库。"""
    asyncio.run(_process(task_id))


async def _process(task_id: int) -> None:
    s = get_settings()
    with SessionLocal() as db:
        task = document_task_repo.get_task(db, task_id)
        if task is None:
            return
        try:
            document_task_repo.update_status(db, task, "processing")
            document = db.get(Document, task.document_id)
            with open(task.file_path, "rb") as fh:
                content = fh.read()
            text = parse_file(content, document.filename)
            chunks = split_text(text, s.chunk_size, s.chunk_overlap)
            chunks = [c for c in chunks if not is_prompt_injection(c)]
            if not chunks:
                raise ValueError("文档包含可疑注入内容，已拦截")
            vectors = await embed_texts(chunks)
            document_repo.add_chunks(db, document.id, chunks)
            vector_repo.upsert_document_chunks(
                document.id, document.user_id, chunks, vectors
            )
            document.chunk_count = len(chunks)
            db.commit()
            document_task_repo.update_status(db, task, "completed")
            if os.path.exists(task.file_path):
                os.remove(task.file_path)
        except Exception as exc:
            document_task_repo.update_status(db, task, "failed", str(exc))
