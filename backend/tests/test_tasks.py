import asyncio
import pathlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.entities import Document, DocumentChunk, DocumentTask, User
from app.repositories import document_task_repo
from app.services import document_processing


def test_process_document_task(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_maker = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(document_processing, "SessionLocal", test_session_maker)

    async def fake_embed(texts):
        return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr(document_processing, "embed_texts", fake_embed)
    monkeypatch.setattr(
        document_processing.vector_repo,
        "upsert_document_chunks",
        lambda *args, **kwargs: None,
    )

    with test_session_maker() as db:
        user = User(username="u", password_hash="")
        db.add(user)
        db.commit()
        doc = Document(
            user_id=user.id,
            filename="知识库.txt",
            file_type="txt",
            file_size=1,
            chunk_count=0,
        )
        db.add(doc)
        db.commit()
        file_path = tmp_path / "doc.txt"
        file_path.write_text("苹果是红色的，香蕉是黄色的。", encoding="utf-8")
        task = document_task_repo.create_task(db, doc.id, str(file_path))

    document_processing.process_document_task(task.id)

    with test_session_maker() as db:
        updated_task = document_task_repo.get_task(db, task.id)
        updated_doc = db.get(Document, doc.id)
        assert updated_task.status == "completed"
        assert updated_doc.chunk_count > 0
        assert db.query(DocumentChunk).count() == updated_doc.chunk_count
        assert not file_path.exists()
    engine.dispose()
