from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_unified_format() -> None:
    """验证 /api/health 返回统一格式，且包含数据库与向量库探测结果。

    TestClient 会启动一个内存中的 FastAPI 实例，不需要真的开端口，
    适合作为接口回归测试。
    """
    client = TestClient(app)
    resp = client.get("/api/health")

    # HTTP 状态必须是 200，body 必须是约定好的 {code, message, data} 结构
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["service"] == "aigc-backend"
    # 数据库与 Qdrant 字段必须存在（值可以是 ok/error，取决于容器状态）
    assert "database" in body["data"]
    assert "qdrant" in body["data"]
