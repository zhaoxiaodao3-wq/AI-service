# 02 · API Key 加密存储（Fernet）

## 做了什么

`backend/app/core/security.py` 提供两个函数：

- `encrypt_secret(value)`：把明文 API Key 加密成 Fernet 密文。
- `decrypt_secret(value)`：把密文解密回明文。

模型表 `ai_models` 只存 `api_key_encrypted` 密文，任何接口都不会把明文 Key 返回给前端。

## 为什么

API Key 是访问大模型服务的凭证，明文落库等于把“家门钥匙”写在门口。数据库一旦泄露，所有模型额度都会被盗用。Fernet 是对称加密方案，加密和解密用同一个密钥，简单可靠，适合本地项目练手；生产环境可在此基础上加 KMS/密钥轮换。

## 原理

### Fernet

`cryptography.fernet.Fernet` 是基于 AES-CBC + HMAC 的对称加密，密文自带版本、时间戳、签名，能防篡改。

```python
def _fernet() -> Fernet:
    key = get_settings().secret_key
    return Fernet(key.encode("utf-8"))
```

`SECRET_KEY` 必须是合法的 Fernet key（32 字节做 base64 编码后的字符串）。项目提供了开发默认值，`.env.example` 也同步了。

### 加解密流程

```text
明文 Key ──encrypt_secret──▶ ai_models.api_key_encrypted
ai_models.api_key_encrypted ──decrypt_secret──▶ 调用模型时使用
```

空字符串直接返回空串，避免把空值加密成无意义密文。

## 命令解释

```powershell
docker exec aigc-postgres psql -U aigc_user -d aigc_chat -c "SELECT name, api_key_encrypted FROM ai_models LIMIT 3;"
```

查询结果中的 `api_key_encrypted` 是类似 `gAAAAABqfsBP...` 的密文，而不是明文 Key。

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/test_persistence.py::test_secret_encryption_roundtrip -q
```

单独验证加密回环：加密后不等于明文，解密后等于原值。

## 避坑

- `SECRET_KEY` 一旦更换，旧密文将无法解密，生产环境必须妥善备份并做密钥轮换。
- 不要把 `.env` 里的真实 Key 提交到 git；`.env` 已在 `.gitignore` 中。
- Fernet 对密钥格式敏感，手工抄错一个字符就会报 `InvalidToken`。
- 本阶段所有模型共用 `.env` 的一个 Key 做种子；多模型独立 Key 管理放到阶段 5。
