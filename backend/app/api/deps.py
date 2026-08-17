from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.entities import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """从 Bearer Token 解析当前用户；失败返回 401。"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期")
    user = db.query(User).filter_by(id=int(payload.get("sub", 0))).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
