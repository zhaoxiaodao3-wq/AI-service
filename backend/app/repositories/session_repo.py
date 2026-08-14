from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import ChatSession


def list_sessions(db: Session, user_id: int) -> list[ChatSession]:
    """按更新时间倒序返回用户会话。"""
    return (
        db.query(ChatSession)
        .filter_by(user_id=user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_session(db: Session, session_id: int, user_id: int) -> ChatSession | None:
    """按 ID 与用户查询会话，避免跨用户访问。"""
    return db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()


def create_session(
    db: Session, user_id: int, title: str, model: str | None
) -> ChatSession:
    chat_session = ChatSession(user_id=user_id, title=title, model=model)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return chat_session


def rename_session(db: Session, chat_session: ChatSession, title: str) -> ChatSession:
    chat_session.title = title
    db.commit()
    db.refresh(chat_session)
    return chat_session


def delete_session(db: Session, chat_session: ChatSession) -> None:
    """删除会话；消息通过 cascade 一并删除。"""
    db.delete(chat_session)
    db.commit()


def touch_session(db: Session, session_id: int) -> None:
    """消息变动时刷新会话更新时间，让活跃会话排到列表前面。"""
    db.query(ChatSession).filter_by(id=session_id).update(
        {"updated_at": datetime.utcnow()}
    )
