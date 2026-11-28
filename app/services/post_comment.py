from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_comment import PostComment
from app.schemas.post_comment import PostCommentCreate, PostCommentUpdate


async def get_post_comment_by_id(
    session: AsyncSession,
    comment_id: int,
) -> PostComment | None:
    return await session.get(PostComment, comment_id)


async def get_post_comments(
    session: AsyncSession,
    post_id: int,
    offset: int,
    limit: int,
) -> Sequence[PostComment]:
    statement = (
        select(PostComment)
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at, PostComment.id)
        .offset(offset)
        .limit(limit)
    )
    return (await session.scalars(statement)).all()


async def create_post_comment(
    session: AsyncSession,
    post_id: int,
    user_id: int,
    data: PostCommentCreate,
) -> PostComment:
    # Автор определяется по токену
    # Пост по url запроса
    comment = PostComment(
        post_id=post_id,
        user_id=user_id,
        content_text=data.content_text,
    )

    session.add(comment)
    await session.commit()
    return comment


async def update_post_comment(
    session: AsyncSession,
    comment: PostComment,
    data: PostCommentUpdate,
) -> PostComment:
    comment.content_text = data.content_text
    await session.commit()
    return comment


async def delete_post_comment(
    session: AsyncSession,
    comment: PostComment,
) -> None:
    await session.delete(comment)
    await session.commit()
