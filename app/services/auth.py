from asyncio import to_thread

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserRegister


class LoginAlreadyExistsError(Exception):
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
        hash_password, data.password
    )  # Хэширование переданного пароля

    user = User(
        login=data.login,
        password_hash=password_hash,
        displayed_name=data.displayed_name,
        about=data.about,
    )

    session.add(user)

    try:
        await session.commit()
    # Обработка ситуации когда два пользователя паытаются одновременно зарегистрировать один логин
    except IntegrityError as error:
        await session.rollback()

        existing_user_id = await session.scalar(
            select(User.id).where(User.login == data.login)
        )

        if existing_user_id is not None:
            raise LoginAlreadyExistsError("Login is already taken") from error
        raise

    return user
