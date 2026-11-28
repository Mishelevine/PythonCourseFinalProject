from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_category import PostCategory
from app.schemas.post_category import PostCategoryUpdate


class CategoryNameAlreadyExistsError(Exception):
    pass


async def get_post_category_by_id(
    session: AsyncSession,
    post_category_id: int,
) -> PostCategory | None:
    return await session.get(PostCategory, post_category_id)


async def get_post_categories(
    session: AsyncSession,
    offset: int,
    limit: int,
) -> Sequence[PostCategory]:
    statement = (
        select(PostCategory)
        .order_by(PostCategory.id)
        .offset(offset)
        .limit(limit)
    )
    return (await session.scalars(statement)).all()


async def create_post_category(
    session: AsyncSession,
    category_name: str,
) -> PostCategory:
    category = PostCategory(category_name=category_name)

    session.add(category)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()

        existing_category_id = await session.scalar(
            select(PostCategory.id).where(
                PostCategory.category_name == category_name
            )
        )
        if existing_category_id is not None:
            raise CategoryNameAlreadyExistsError(
                "Category name is already taken"
            ) from error
        raise

    return category


async def update_post_category(
    session: AsyncSession,
    post_category: PostCategory,
    data: PostCategoryUpdate,
) -> PostCategory:
    # Обновляем переданные поля
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post_category, field, value)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()

        existing_category_id = await session.scalar(
            select(PostCategory.id).where(
                PostCategory.category_name == data.category_name
            )
        )
        if existing_category_id is not None:
            raise CategoryNameAlreadyExistsError(
                "Category name is already taken"
            ) from error
        raise

    return post_category


async def delete_post_category(
    session: AsyncSession, post_category: PostCategory
) -> None:
    await session.delete(post_category)
    await session.commit()
