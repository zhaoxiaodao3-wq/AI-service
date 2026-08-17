import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import decrypt_secret, encrypt_secret
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.entities import AiModel, ChatMessage, ChatSession, ModelCall, User


@pytest.fixture()
def db_session():
    """SQLite 内存库，隔离测试数据。"""
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


def test_session_crud(client, db_session):
    """会话新建/列表/重命名/消息查询/删除全链路。"""
    resp = client.post("/api/sessions", json={"title": "测试会话"})
    assert resp.status_code == 200
    session = resp.json()["data"]["session"]
    session_id = session["id"]
    assert session["title"] == "测试会话"

    resp = client.get("/api/sessions")
    assert len(resp.json()["data"]["sessions"]) == 1

    resp = client.patch(f"/api/sessions/{session_id}", json={"title": "改名"})
    assert resp.json()["data"]["session"]["title"] == "改名"

    from app.services import message_service

    message_service.add_message(db_session, session_id, "user", "你好")
    resp = client.get(f"/api/sessions/{session_id}/messages")
    messages = resp.json()["data"]["messages"]
    assert messages[0]["content"] == "你好"

    resp = client.delete(f"/api/sessions/{session_id}")
    assert resp.json()["data"]["deleted"] is True
    assert db_session.query(ChatSession).count() == 0


def test_models_from_db(client, db_session):
    """模型下拉从数据库读取启用模型。"""
    db_session.add(
        AiModel(name="glm-4-flash", provider="zhipu", enabled=True, weight=0)
    )
    db_session.add(
        AiModel(name="deepseek-chat", provider="deepseek", enabled=True, weight=1)
    )
    db_session.commit()

    resp = client.get("/api/models")
    assert resp.status_code == 200
    models = resp.json()["data"]["models"]
    assert models == ["glm-4-flash", "deepseek-chat"]


def test_secret_encryption_roundtrip():
    """API Key 密文存储且可解密回原值。"""
    raw = "sk-test-123456"
    encrypted = encrypt_secret(raw)
    assert encrypted != raw
    assert decrypt_secret(encrypted) == raw


def test_stats_api(client, db_session):
    """统计接口应返回调用次数、成功率、Token 与按模型分布。"""
    db_session.add(
        ModelCall(model="glm-4-flash", success=True, token_count=10, duration_ms=100)
    )
    db_session.add(
        ModelCall(model="glm-4-flash", success=False, token_count=None, duration_ms=50)
    )
    db_session.commit()

    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_calls"] == 2
    assert data["success_rate"] == 0.5
    assert data["total_tokens"] == 10
    assert data["by_model"]["glm-4-flash"]["calls"] == 2


def test_rate_limit_returns_429():
    """chat 接口超过限流阈值应返回 429。"""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.rate_limit import RateLimitMiddleware

    app = FastAPI()

    @app.post("/api/chat/stream")
    def fake_chat():
        return {"ok": True}

    app.add_middleware(RateLimitMiddleware, limit=2, window=60)
    client = TestClient(app)
    assert client.post("/api/chat/stream").status_code == 200
    assert client.post("/api/chat/stream").status_code == 200
    assert client.post("/api/chat/stream").status_code == 429


def test_chat_persists_messages(monkeypatch, client):
    """chat 带 session_id 时自动保存 user 与 assistant 消息。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_maker = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    with test_session_maker() as seed:
        seed.add(User(username="local", password_hash=""))
        seed.commit()
        chat_session = ChatSession(user_id=1, title="流式会话", model=None)
        seed.add(chat_session)
        seed.commit()
        session_id = chat_session.id

    monkeypatch.setattr("app.api.chat.SessionLocal", test_session_maker)

    async def fake_embed(texts):
        return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr("app.api.chat.embed_texts", fake_embed)
    monkeypatch.setattr("app.services.chat_service.embed_texts", fake_embed)
    monkeypatch.setattr(
        "app.services.chat_service.vector_repo.search_memories",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "app.api.chat.vector_repo.upsert_memory",
        lambda *args, **kwargs: None,
    )

    async def fake_stream(request):
        yield "你"
        yield "好"

    monkeypatch.setattr("app.services.chat_service.stream_chat", fake_stream)

    resp = client.post(
        "/api/chat/stream",
        json={
            "messages": [{"role": "user", "content": "hi"}],
            "model": "glm-4-flash",
            "session_id": session_id,
        },
    )
    assert resp.status_code == 200

    with test_session_maker() as check:
        messages = check.query(ChatMessage).order_by(ChatMessage.id).all()
        assert [m.role for m in messages] == ["user", "assistant"]
        assert messages[0].content == "hi"
        assert messages[1].content == "你好"
