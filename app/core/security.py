import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Используем рекомендованный метод хэширования паролей - Argon2
password_hasher = PasswordHash.recommended()


# Хэширование
def hash_password(password: str) -> str:
    return password_hasher.hash(password)


# Проверка проля с хэшем
def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


# Access token
def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256",
    )


# Проверка Access Token пользователя
def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "exp"]},
    )

    # sub содержит user_id
    return int(payload["sub"])


# Refresh token


# Генерация строки из 32 байт
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


# Хэширование строки
def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
