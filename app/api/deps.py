from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.database import async_session_factory
from app.models.user import User

# Схема для извлечения токена из запроса к API
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    auto_error=False,
)


class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },  # Сообщаем клиенту, какая авторизация требуется
        )


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    if token is None:
        raise UnauthorizedError()

    try:
        # Изпользуем полученный из заголовка токен
        user_id = decode_access_token(token)
    except (InvalidTokenError, ValueError) as error:
        raise UnauthorizedError() from error

    user = await session.get(User, user_id)

    if user is None:
        raise UnauthorizedError()

    return user


# Без токена возвращаем None чтобы неавторизованные
# пользовтели также могли читать статьи, комментарии и так далее
async def get_optional_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    if token is None:
        return None
    return await get_current_user(token, session)


# Функция для проверки роли администратора 
# у текущего пользователя по access токену
async def get_current_admin(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    if token is None:
        raise UnauthorizedError()

    try:
        # Изпользуем полученный из заголовка токен
        user_id = decode_access_token(token)
    except (InvalidTokenError, ValueError) as error:
        raise UnauthorizedError() from error

    user = await session.get(User, user_id)

    if user is None:
        raise UnauthorizedError()

    if user.user_role != "admin":
        raise HTTPException(403, "Forbidden")

    return user
