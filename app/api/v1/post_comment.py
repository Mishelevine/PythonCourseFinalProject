from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_optional_current_user,
    get_post_by_id,
    get_readable_post,
    get_session,
)
from app.models.post import Post, PostStatus
from app.models.post_comment import PostComment
from app.models.user import User, UserRole
from app.schemas.post_comment import (
    PostCommentCreate,
    PostCommentResponse,
    PostCommentUpdate,
)
from app.services.post_comment import (
    create_post_comment as create_post_comment_db,
)
from app.services.post_comment import (
    delete_post_comment,
    get_post_comments,
    update_post_comment,
)
from app.services.post_comment import (
    get_post_comment_by_id as get_comment_db,
)

router = APIRouter(tags=["posts-comments"])


# Получить комментарий по id
async def get_comment_by_id(
    comment_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PostComment:
    comment = await get_comment_db(session, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


async def get_readable_comment(
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    comment: Annotated[PostComment, Depends(get_comment_by_id)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PostComment:
    # Комментарий доступен только тем, кому доступен сам пост
    post = await get_post_by_id(comment.post_id, session)
    await get_readable_post(current_user, post)
    return comment


async def get_editable_comment(
    current_user: Annotated[User, Depends(get_current_user)],
    comment: Annotated[PostComment, Depends(get_readable_comment)],
) -> PostComment:
    # Редактировать комментарий может только его автор
    if current_user.id != comment.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return comment


async def get_deletable_comment(
    current_user: Annotated[User, Depends(get_current_user)],
    comment: Annotated[PostComment, Depends(get_readable_comment)],
) -> PostComment:
    # Удалить комментарий может его автор или администратор
    if (
        current_user.id != comment.user_id
        and current_user.user_role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return comment


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[PostCommentResponse],
    summary="Получение списка комментариев к посту",
)
async def list_post_comments(
    session: Annotated[AsyncSession, Depends(get_session)],
    post: Annotated[Post, Depends(get_readable_post)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await get_post_comments(session, post.id, offset, limit)


@router.post(
    "/posts/{post_id}/comments",
    status_code=201,
    response_model=PostCommentResponse,
    summary="Создание комментария к посту",
)
async def create_post_comment(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    post: Annotated[Post, Depends(get_readable_post)],
    data: PostCommentCreate,
):
    # Новые комментарии разрешены только у опубликованных постов
    if post.status != PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=403,
            detail="Comments are only allowed on published posts",
        )
    return await create_post_comment_db(session, post.id, user.id, data)


@router.get(
    "/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Получение информации о комментарии",
)
async def get_comment(
    comment: Annotated[PostComment, Depends(get_readable_comment)],
):
    return comment


@router.patch(
    "/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Изменение текста комментария",
)
async def patch_comment(
    session: Annotated[AsyncSession, Depends(get_session)],
    comment: Annotated[PostComment, Depends(get_editable_comment)],
    data: PostCommentUpdate,
):
    return await update_post_comment(session, comment, data)


@router.delete(
    "/comments/{comment_id}",
    status_code=204,
    summary="Удаление комментария",
)
async def remove_comment(
    session: Annotated[AsyncSession, Depends(get_session)],
    comment: Annotated[PostComment, Depends(get_deletable_comment)],
):
    return await delete_post_comment(session, comment)
