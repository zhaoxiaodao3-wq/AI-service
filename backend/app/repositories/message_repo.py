from sqlalchemy.orm import Session

from app.models.entities import ChatMessage, ChatSession
from app.repositories.session_repo import touch_session


def list_messages(db: Session, session_id: int) -> list[ChatMessage]:
    """按创建顺序返回会话消息。"""
    return (
        db.query(ChatMessage)
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )


def add_message(
    db: Session,
    session_id: int,
    role: str,
    content: str,
    token_count: int | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        token_count=token_count,
    )
    db.add(message)
    touch_session(db, session_id)
    db.commit()
    db.refresh(message)
    return message
