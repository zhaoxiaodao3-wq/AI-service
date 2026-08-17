from app.core.exceptions import AppError
from app.models.entities import ChatSession
from app.repositories import session_repo


def list_sessions(db, user_id: int) -> list[ChatSession]:
    """返回指定用户的会话列表。"""
    return session_repo.list_sessions(db, user_id)


def create_session(
    db, user_id: int, title: str | None = None, model: str | None = None
) -> ChatSession:
    if not title:
        count = len(session_repo.list_sessions(db, user_id))
        title = f"新会话 {count + 1}"
    return session_repo.create_session(db, user_id, title, model)


def get_session(db, session_id: int, user_id: int) -> ChatSession:
    chat_session = session_repo.get_session(db, session_id, user_id)
    if chat_session is None:
        raise AppError(404, "会话不存在")
    return chat_session


def rename_session(db, session_id: int, title: str, user_id: int) -> ChatSession:
    chat_session = get_session(db, session_id, user_id)
    return session_repo.rename_session(db, chat_session, title)


def delete_session(db, session_id: int, user_id: int) -> None:
    chat_session = get_session(db, session_id, user_id)
    session_repo.delete_session(db, chat_session)
