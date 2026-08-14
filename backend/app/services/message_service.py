from app.models.entities import ChatMessage
from app.repositories import message_repo


def list_messages(db, session_id: int) -> list[ChatMessage]:
    return message_repo.list_messages(db, session_id)


def add_message(
    db,
    session_id: int,
    role: str,
    content: str,
    token_count: int | None = None,
) -> ChatMessage:
    return message_repo.add_message(db, session_id, role, content, token_count)
