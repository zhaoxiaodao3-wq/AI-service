import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.entities import Document, User
from app.services.chunker import split_text
from app.services.document_service import build_rag_messages


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    session.add(User(username="local", password_hash=""))
    session.commit()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_split_text_with_overlap():
    chunks = split_text("abcdefghij", chunk_size=5, chunk_overlap=2)
    assert chunks == ["abcde", "defgh", "ghij"]


def test_build_rag_messages_injects_context():
    class Hit:
        payload = {"text": "苹果是红色的"}

    messages = [
        {"role": "system", "content": "旧的系统提示"},
        {"role": "user", "content": "苹果是什么颜色？"},
    ]
    result = build_rag_messages(messages, [Hit()])
    assert result[0]["role"] == "system"
    assert "苹果是红色的" in result[0]["content"]
    assert result[-1] == messages[-1]
    assert len(result) == 2


def test_upload_document_txt(monkeypatch, client):
    async def fake_embed(texts):
        return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr("app.api.documents.embed_texts", fake_embed)
    monkeypatch.setattr(
        "app.api.documents.vector_repo.upsert_document_chunks",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.api.documents.vector_repo.delete_document_vectors",
        lambda *args, **kwargs: None,
    )

    resp = client.post(
        "/api/documents",
        files={
            "file": (
                "知识库.txt",
                "你好世界，这是知识库内容。苹果是红色的。".encode("utf-8"),
                "text/plain",
            )
        },
    )
    assert resp.status_code == 200
    document = resp.json()["data"]["document"]
    assert document["filename"] == "知识库.txt"
    assert document["chunk_count"] > 0

    assert client.get("/api/documents").json()["data"]["documents"][0]["id"] == document["id"]
    resp = client.delete(f"/api/documents/{document['id']}")
    assert resp.json()["data"]["deleted"] is True


def test_local_embedding_deterministic():
    from app.services.local_embedding import embed_text

    vector = embed_text("苹果是红色的", dimensions=1024)
    assert len(vector) == 1024
    assert abs(sum(v * v for v in vector) - 1.0) < 1e-6
    assert vector == embed_text("苹果是红色的", dimensions=1024)
