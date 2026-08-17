import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.db.base import Base
from app.main import app
from app.models.entities import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    user = User(username="test", password_hash="")
    session.add(user)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user
    yield TestClient(app)
    app.dependency_overrides.clear()
    session.close()
    engine.dispose()


def test_chat_stream_emits_delta_and_done(monkeypatch, client):
    """验证 SSE 接口依次输出 delta/delta/done 事件。"""

    async def fake_stream(request):
        yield "你"
        yield "好"

    monkeypatch.setattr(
        "app.services.chat_service.stream_chat", fake_stream
    )
    resp = client.post(
        "/api/chat/stream",
        json={
            "messages": [{"role": "user", "content": "hi"}],
            "model": "glm-4-flash",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    events = [
        json.loads(line[5:])
        for line in resp.text.splitlines()
        if line.startswith("data: ")
    ]
    kinds = [e["type"] for e in events]
    assert kinds == ["delta", "delta", "done"]


def test_chat_stream_invalid_body_returns_422(client):
    """空请求体应返回 422 校验错误。"""
    resp = client.post("/api/chat/stream", json={})
    assert resp.status_code == 422


def test_chat_stream_emits_error_on_model_error(monkeypatch, client):
    """适配层抛 ModelError 时，SSE 应输出 error 事件而不是 500。"""
    from app.adapters.model_adapter import ModelError

    async def fake_stream(request):
        raise ModelError("invalid_key", "API Key 无效")
        yield ""  # pragma: no cover - 让函数成为 async generator

    monkeypatch.setattr(
        "app.services.chat_service.stream_chat", fake_stream
    )
    resp = client.post(
        "/api/chat/stream",
        json={
            "messages": [{"role": "user", "content": "hi"}],
            "model": "glm-4-flash",
        },
    )
    assert resp.status_code == 200
    events = [
        json.loads(line[5:])
        for line in resp.text.splitlines()
        if line.startswith("data: ")
    ]
    assert events[0]["type"] == "error"
    assert events[0]["code"] == "invalid_key"
