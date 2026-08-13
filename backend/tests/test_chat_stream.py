import json

from fastapi.testclient import TestClient

from app.main import app


def test_chat_stream_emits_delta_and_done(monkeypatch):
    """验证 SSE 接口依次输出 delta/delta/done 事件。

    mock 掉适配层 stream_chat，不真实调用模型。
    """

    async def fake_stream(request):
        yield "你"
        yield "好"

    monkeypatch.setattr(
        "app.services.chat_service.stream_chat", fake_stream
    )
    client = TestClient(app)
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


def test_chat_stream_invalid_body_returns_422():
    """空请求体应返回 422 校验错误。"""
    client = TestClient(app)
    resp = client.post("/api/chat/stream", json={})
    assert resp.status_code == 422


def test_chat_stream_emits_error_on_model_error(monkeypatch):
    """适配层抛 ModelError 时，SSE 应输出 error 事件而不是 500。"""
    from app.adapters.model_adapter import ModelError

    async def fake_stream(request):
        # 含 yield 才能成为异步生成器；迭代第一项时抛错，模拟真实断流
        raise ModelError("invalid_key", "API Key 无效")
        yield ""  # pragma: no cover - 让函数成为 async generator

    monkeypatch.setattr(
        "app.services.chat_service.stream_chat", fake_stream
    )
    client = TestClient(app)
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
