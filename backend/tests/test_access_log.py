import logging

from fastapi.testclient import TestClient

from app.main import app


def test_access_log_records_request_and_response(caplog, monkeypatch):
    """普通接口应产生请求开始/请求结束日志。"""
    monkeypatch.setattr(
        "app.api.models.list_models",
        lambda db: (["glm-4-flash"], "glm-4-flash"),
    )
    with caplog.at_level(logging.INFO, logger="app.access"):
        client = TestClient(app)
        resp = client.get("/api/models")

    assert resp.status_code == 200
    messages = [r.message for r in caplog.records if r.name == "app.access"]
    assert any(
        "request start method=GET path=/api/models" in m for m in messages
    )
    assert any(
        "request end method=GET path=/api/models" in m and "status=200" in m
        for m in messages
    )


def test_chat_stream_logs_start_and_finish(monkeypatch, caplog):
    """SSE 对话应记录 start/finish 与返回字符数。"""

    async def fake_stream(request):
        yield "你"
        yield "好"

    monkeypatch.setattr("app.services.chat_service.stream_chat", fake_stream)

    with caplog.at_level(logging.INFO, logger="app.chat"):
        client = TestClient(app)
        resp = client.post(
            "/api/chat/stream",
            json={
                "messages": [{"role": "user", "content": "hi"}],
                "model": "glm-4-flash",
            },
        )

    assert resp.status_code == 200
    chat_messages = [r.message for r in caplog.records if r.name == "app.chat"]
    assert any("chat_stream start messages=1" in m for m in chat_messages)
    assert any(
        "chat_stream finish" in m and "chars=2" in m for m in chat_messages
    )
    delta_logs = [m for m in chat_messages if "chat_stream delta" in m]
    assert len(delta_logs) == 2
    assert "chunk_chars=1" in delta_logs[0]
    assert "total_chars=1" in delta_logs[0]
    assert "total_chars=2" in delta_logs[1]
