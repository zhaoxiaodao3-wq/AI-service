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
