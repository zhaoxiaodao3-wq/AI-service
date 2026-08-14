from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import ok
from app.db.session import get_db
from app.schemas.session import MessageOut, SessionCreate, SessionOut, SessionRename
from app.services import message_service, session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _session_payload(chat_session) -> dict:
    return SessionOut.model_validate(chat_session).model_dump(mode="json")


@router.get("")
def list_sessions(db: Session = Depends(get_db)):
    """列出默认用户全部会话，按最近更新排序。"""
    sessions = session_service.list_sessions(db)
    return ok({"sessions": [_session_payload(s) for s in sessions]})


@router.post("")
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    """新建会话；标题缺省时自动生成“新会话 N”。"""
    chat_session = session_service.create_session(db, payload.title, payload.model)
    return ok({"session": _session_payload(chat_session)})


@router.get("/{session_id}/messages")
def list_messages(session_id: int, db: Session = Depends(get_db)):
    """查询会话历史消息，按创建顺序返回。"""
    chat_session = session_service.get_session(db, session_id)
    messages = message_service.list_messages(db, chat_session.id)
    return ok(
        {
            "messages": [
                MessageOut.model_validate(m).model_dump(mode="json")
                for m in messages
            ]
        }
    )


@router.patch("/{session_id}")
def rename_session(
    session_id: int, payload: SessionRename, db: Session = Depends(get_db)
):
    """重命名会话。"""
    chat_session = session_service.rename_session(db, session_id, payload.title)
    return ok({"session": _session_payload(chat_session)})


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """删除会话及其消息。"""
    session_service.delete_session(db, session_id)
    return ok({"deleted": True})
