from sqlalchemy.orm import Session

from app.models.entities import User

DEFAULT_USERNAME = "local"


def get_default_user(db: Session) -> User:
    """获取默认本地用户；不存在时自动创建（幂等）。"""
    user = db.query(User).filter_by(username=DEFAULT_USERNAME).first()
    if user is None:
        user = User(username=DEFAULT_USERNAME, password_hash="")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
