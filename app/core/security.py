from pwdlib import PasswordHash

# Используем рекомендованный метод хэширования паролей - Argon2
password_hasher = PasswordHash.recommended()


# Хэширование
def hash_password(password: str) -> str:
    return password_hasher.hash(password)


# Проверка проля с хэшем
def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)
