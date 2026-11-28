from collections.abc import Sequence

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_likes import PostLike


async def create_post_like(
    session: AsyncSession,
    post_id: int,
    user_id: int,
) -> bool:
    # Повторные и одновременные запросы не создают второй лайк
    statement = (
        insert(PostLike)
        .values(post_id=post_id, user_id=user_id)
        .on_conflict_do_nothing(index_elements=["post_id", "user_id"])
        .returning(PostLike.id)
    )
    like_id = await session.scalar(statement)
    await session.commit()
    return like_id is not None


async def delete_post_like(
    session: AsyncSession,
    post_id: int,
    user_id: int,
) -> None:
    # Удаляем только лайк текущего пользователя
    statement = delete(PostLike).where(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id,
    )
    await session.execute(statement)
    await session.commit()


async def get_post_like_stats(
    session: AsyncSession,
    post_ids: Sequence[int],
    current_user_id: int | None = None,
) -> dict[int, dict[str, int | bool]]:
    if not post_ids:
        return {}

    # Получаем количество лайков и свой лайк сразу для всех постов страницы
    statement = (
        select(
            PostLike.post_id,
            func.count(PostLike.id),
            func.max(case((PostLike.user_id == current_user_id, 1), else_=0)),
        )
        .where(PostLike.post_id.in_(post_ids))
        .group_by(PostLike.post_id)
    )
    result = await session.execute(statement)
    return {
        post_id: {"likes_count": likes_count, "is_liked": bool(is_liked)}
        for post_id, likes_count, is_liked in result
    }
