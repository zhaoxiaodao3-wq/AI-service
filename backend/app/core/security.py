import datetime
import hashlib
import secrets

import bcrypt
import jwt
from cryptography.fernet import Fernet

from app.core.config import get_settings


def _fernet() -> Fernet:
    """根据 SECRET_KEY 构造 Fernet 实例。"""
    key = get_settings().secret_key
    return Fernet(key.encode("utf-8"))


def encrypt_secret(value: str) -> str:
    """加密敏感字段（如 API Key），空值直接返回空串。"""
    if not value:
        return ""
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    """解密敏感字段，空值直接返回空串。"""
    if not value:
        return ""
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def hash_password(password: str) -> str:
    """bcrypt 哈希密码，不落明文。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码；哈希非法时返回 False 而不是抛错。"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    s = get_settings()
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=s.access_token_expire_minutes),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    s = get_settings()
    try:
        return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
    except jwt.PyJWTError:
        return None


def create_refresh_token() -> str:
    """生成不可猜测的刷新令牌原文。"""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """刷新令牌只存哈希，即使库泄露也不能直接使用。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
