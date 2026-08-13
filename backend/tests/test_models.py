from fastapi.testclient import TestClient

from app.main import app


def test_models_returns_list():
    """验证 GET /api/models 返回模式、模型清单与默认模型。"""
    client = TestClient(app)
    resp = client.get("/api/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert "mode" in body["data"]  # official / proxy
    assert isinstance(body["data"]["models"], list)
    assert len(body["data"]["models"]) > 0
    assert body["data"]["default_model"]
