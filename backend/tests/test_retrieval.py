import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.entities import Document, DocumentChunk, User
from app.repositories import document_chunk_repo, document_repo
from app.services.retrieval_service import RagHit


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    yield session
    session.close()
    engine.dispose()


def test_keyword_search_and_filenames(db_session):
    user = User(username="u1", password_hash="")
    db_session.add(user)
    db_session.commit()
    doc = Document(
        user_id=user.id,
        filename="知识库.txt",
        file_type="txt",
        file_size=1,
        chunk_count=2,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.add(
        DocumentChunk(document_id=doc.id, chunk_index=0, content="苹果是红色的")
    )
    db_session.add(
        DocumentChunk(document_id=doc.id, chunk_index=1, content="香蕉是黄色的")
    )
    db_session.commit()

    rows = document_chunk_repo.search_keyword(db_session, user.id, "苹果", limit=5)
    assert len(rows) == 1
    assert rows[0].chunk_index == 0

    names = document_repo.get_filenames_by_ids(db_session, [doc.id])
    assert names[doc.id] == "知识库.txt"

    hit = RagHit(doc_id=doc.id, chunk_index=0, text="x")
    assert hit.payload["doc_id"] == doc.id
    assert hit.payload["text"] == "x"
