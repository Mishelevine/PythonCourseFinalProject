from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    return await session.get(User, user_id)


async def get_users(
    session: AsyncSession,
    offset: int,
    limit: int,
) -> Sequence[User]:
    statement = select(User).order_by(User.id).offset(offset).limit(limit)
    return (await session.scalars(statement)).all()


async def update_user(
    session: AsyncSession,
    user: User,
    data: UserUpdate,
) -> User:
    # Обновляем переданные поля
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()
