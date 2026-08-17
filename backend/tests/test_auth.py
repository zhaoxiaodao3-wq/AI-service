import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.entities import ChatSession, User


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


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _register(client, username="alice", password="secret123"):
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["data"]["tokens"]


def test_register_login_me_refresh_logout(client):
    tokens = _register(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["user"]["username"] == "alice"

    login = client.post(
        "/api/auth/login", json={"username": "alice", "password": "secret123"}
    )
    assert login.status_code == 200

    refresh = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 200
    new_tokens = refresh.json()["data"]["tokens"]

    # 旧 refresh 已被轮换，不能再用
    old = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert old.status_code == 401

    logout = client.post(
        "/api/auth/logout", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert logout.status_code == 200
    after_logout = client.post(
        "/api/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert after_logout.status_code == 401


def test_login_wrong_password(client):
    _register(client)
    resp = client.post(
        "/api/auth/login", json={"username": "alice", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_user_isolation(client, db_session):
    alice = _register(client, "alice")
    bob = _register(client, "bob")

    alice_headers = {"Authorization": f"Bearer {alice['access_token']}"}
    bob_headers = {"Authorization": f"Bearer {bob['access_token']}"}

    created = client.post("/api/sessions", json={}, headers=alice_headers)
    assert created.status_code == 200
    session_id = created.json()["data"]["session"]["id"]

    bob_list = client.get("/api/sessions", headers=bob_headers)
    assert bob_list.json()["data"]["sessions"] == []

    bob_get = client.get(f"/api/sessions/{session_id}/messages", headers=bob_headers)
    assert bob_get.status_code == 404

    # 未登录访问业务接口应 401
    unauth = client.get("/api/sessions")
    assert unauth.status_code == 401
