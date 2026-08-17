from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.response import ok
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models.entities import RefreshToken, User
from app.repositories import user_repo
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenOut,
    UserOut,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _tokens(db: Session, user: User) -> dict:
    s = get_settings()
    access = create_access_token(user.id)
    refresh = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh),
            expires_at=datetime.utcnow()
            + timedelta(days=s.refresh_token_expire_days),
        )
    )
    db.commit()
    return TokenOut(
        access_token=access,
        refresh_token=refresh,
        user=UserOut.model_validate(user),
    ).model_dump(mode="json")


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户并返回令牌。"""
    if user_repo.get_user_by_username(db, payload.username):
        raise AppError(400, "用户名已存在")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ok({"tokens": _tokens(db, user)})


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """登录并返回访问令牌与刷新令牌。"""
    user = user_repo.get_user_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash or ""):
        raise AppError(401, "用户名或密码错误")
    return ok({"tokens": _tokens(db, user)})


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """刷新令牌轮换：旧 refresh 撤销，返回新令牌对。"""
    token_hash = hash_refresh_token(payload.refresh_token)
    record = (
        db.query(RefreshToken).filter_by(token_hash=token_hash).first()
    )
    if (
        record is None
        or record.revoked
        or record.expires_at < datetime.utcnow()
    ):
        raise AppError(401, "刷新令牌无效")
    user = db.query(User).filter_by(id=record.user_id).first()
    if user is None:
        raise AppError(401, "用户不存在")
    record.revoked = True
    db.commit()
    return ok({"tokens": _tokens(db, user)})


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    """撤销刷新令牌，登出。"""
    record = (
        db.query(RefreshToken)
        .filter_by(token_hash=hash_refresh_token(payload.refresh_token))
        .first()
    )
    if record is not None:
        record.revoked = True
        db.commit()
    return ok({"logged_out": True})


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """返回当前登录用户信息。"""
    return ok({"user": UserOut.model_validate(user).model_dump(mode="json")})
