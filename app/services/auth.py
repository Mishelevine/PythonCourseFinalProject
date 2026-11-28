from asyncio import to_thread
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    TokenPairResponse,
    UserLogin,
    UserPasswordUpdate,
    UserRegister,
)


class LoginAlreadyExistsError(Exception):
    pass


class IncorrectLoginOrPassword(Exception):
    pass


class IncorrectCurrentPasswordError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


# Регистрация нового пользователя
async def register_user(
    session: AsyncSession,
    data: UserRegister,
) -> User:
    # Проверка, что такого логина еще нет до хэширования пароля
    existing_user_id = await session.scalar(
        select(User.id).where(User.login == data.login)
    )

    if existing_user_id is not None:
        raise LoginAlreadyExistsError("Login is already taken")

    password_hash = await to_thread(
        hash_password,
        data.password.get_secret_value(),
    )  # Запуск синхронной функции хэширования в отдельном потоке

    # Если пользователь не указал имя профиля, то используем логин
    if data.displayed_name is None:
        data.displayed_name = data.login

    user = User(
        login=data.login,
        password_hash=password_hash,
        first_name=data.first_name,
        last_name=data.last_name,
        displayed_name=data.displayed_name,
        about=data.about,
    )

    session.add(user)

    try:
        await session.commit()
    # Обработка ситуации когда два пользователя
    # паытаются одновременно зарегистрировать один логин
    except IntegrityError as error:
        await session.rollback()

        existing_user_id = await session.scalar(
            select(User.id).where(User.login == data.login)
        )

        if existing_user_id is not None:
            raise LoginAlreadyExistsError("Login is already taken") from error
        raise

    return user


# Вход пользователя
async def login_user(session: AsyncSession, data: UserLogin):
    user = await session.scalar(select(User).where(User.login == data.login))

    # Проверка существования пользователя
    if user is None:
        raise IncorrectLoginOrPassword("Incorrect login or password")

    # Проверка пароля
    password_is_valid = await to_thread(
        verify_password, data.password, user.password_hash
    )

    if not password_is_valid:
        raise IncorrectLoginOrPassword("Incorrect login or password")

    return user


# Функция для смены пароля
async def change_user_password(
    session: AsyncSession,
    user: User,
    data: UserPasswordUpdate,
) -> None:
    # Проверка текущего пароля
    password_is_valid = await to_thread(
        verify_password,
        data.current_password.get_secret_value(),
        user.password_hash,
    )

    if not password_is_valid:
        raise IncorrectCurrentPasswordError("Incorrect current password")

    # Получение хэша нового пароля
    password_hash = await to_thread(
        hash_password,
        data.new_password.get_secret_value(),
    )

    now = datetime.now(UTC).replace(tzinfo=None)

    try:
        user.password_hash = password_hash

        # Отзываем refresh токены пользователя на всех устройствах
        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

        await session.execute(statement)

        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def get_tokens(
    session: AsyncSession,
    user_id: int,
) -> TokenPairResponse:
    # Выпускаем новые токены
    access_token = create_access_token(user_id)
    refresh_token = generate_refresh_token()

    now = datetime.now(UTC).replace(tzinfo=None)

    # Вносим refresh token в БД
    session.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=now
            + timedelta(
                days=settings.refresh_token_expire_days,
            ),
        )
    )

    await session.commit()

    return TokenPairResponse(
        access_token=access_token, refresh_token=refresh_token
    )


async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str,
) -> TokenPairResponse:
    now = datetime.now(UTC).replace(tzinfo=None)

    try:
        # выставляем значение used_at для найденного
        # refrash_token и возвращаем id пользователя
        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == hash_refresh_token(refresh_token),
                RefreshToken.expires_at > now,
                RefreshToken.used_at.is_(None),
                RefreshToken.revoked_at.is_(None),
            )
            .values(used_at=now)
            .returning(RefreshToken.user_id)
        )

        user_id = await session.scalar(statement)

        if user_id is None:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        # Выдаем новые токены по полученному user_id
        return await get_tokens(session, user_id)

    except Exception:
        await session.rollback()
        raise


# Удаление текущего refresh токена
async def revoke_refresh_token(
    session: AsyncSession,
    refresh_token: str,
) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)

    # Находим токен и выставляем revoked_at
    statement = (
        update(RefreshToken)
        .where(
            RefreshToken.token_hash == hash_refresh_token(refresh_token),
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )

    await session.execute(statement)
    await session.commit()
