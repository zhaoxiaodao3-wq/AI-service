from app.core.exceptions import AppError
from app.models.entities import ChatSession
from app.repositories import session_repo, user_repo


def list_sessions(db) -> list[ChatSession]:
    user = user_repo.get_default_user(db)
    return session_repo.list_sessions(db, user.id)


def create_session(
    db, title: str | None = None, model: str | None = None
) -> ChatSession:
    user = user_repo.get_default_user(db)
    if not title:
        count = len(session_repo.list_sessions(db, user.id))
        title = f"新会话 {count + 1}"
    return session_repo.create_session(db, user.id, title, model)


def get_session(db, session_id: int) -> ChatSession:
    user = user_repo.get_default_user(db)
    chat_session = session_repo.get_session(db, session_id, user.id)
    if chat_session is None:
        raise AppError(404, "会话不存在")
    return chat_session


def rename_session(db, session_id: int, title: str) -> ChatSession:
    chat_session = get_session(db, session_id)
    return session_repo.rename_session(db, chat_session, title)


def delete_session(db, session_id: int) -> None:
    chat_session = get_session(db, session_id)
    session_repo.delete_session(db, chat_session)
