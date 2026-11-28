from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostStatus
from app.models.post_category import PostCategory
from app.schemas.post import PostCreate, PostUpdate


class CategoryNotFoundError(Exception):
    pass


async def get_post_by_id(session: AsyncSession, post_id: int) -> Post | None:
    return await session.get(Post, post_id)


async def get_posts(
    session: AsyncSession,
    offset: int,
    limit: int,
    user_id: int | None = None,
    category_id: int | None = None,
) -> Sequence[Post]:
    # В общей ленте показываем только опубликованные посты
    statement = select(Post).where(Post.status == PostStatus.PUBLISHED)
    if user_id is not None:
        statement = statement.where(Post.user_id == user_id)
    if category_id is not None:
        statement = statement.where(Post.category_id == category_id)

    statement = (
        statement.order_by(Post.published_at.desc(), Post.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return (await session.scalars(statement)).all()


async def get_my_posts(
    session: AsyncSession,
    user_id: int,
    offset: int,
    limit: int,
    status: PostStatus | None = None,
) -> Sequence[Post]:
    statement = select(Post).where(Post.user_id == user_id)
    if status is not None:
        statement = statement.where(Post.status == status)

    statement = (
        statement.order_by(Post.created_at.desc(), Post.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return (await session.scalars(statement)).all()


async def check_category(
    session: AsyncSession, category_id: int | None
) -> None:
    if category_id is not None:
        category = await session.get(PostCategory, category_id)
        if category is None:
            raise CategoryNotFoundError("Category not found")


async def create_post(
    session: AsyncSession,
    user_id: int,
    data: PostCreate,
) -> Post:
    await check_category(session, data.category_id)

    # Автор определяется по токену, даты устанавливает сервер
    post = Post(user_id=user_id, **data.model_dump())
    if post.status == PostStatus.PUBLISHED:
        post.published_at = datetime.now(UTC).replace(tzinfo=None)

    session.add(post)
    await session.commit()
    return post


async def update_post(
    session: AsyncSession,
    post: Post,
    data: PostUpdate,
) -> Post:
    fields = data.model_dump(exclude_unset=True)
    if "category_id" in fields:
        await check_category(session, data.category_id)

    # Обновляем только переданные поля
    for field, value in fields.items():
        setattr(post, field, value)

    # Сохраняем дату первой публикации при смене статуса
    if post.status == PostStatus.PUBLISHED and post.published_at is None:
        post.published_at = datetime.now(UTC).replace(tzinfo=None)

    await session.commit()
    return post


async def delete_post(session: AsyncSession, post: Post) -> None:
    await session.delete(post)
    await session.commit()
