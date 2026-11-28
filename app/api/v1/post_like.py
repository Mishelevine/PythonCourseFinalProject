from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_readable_post, get_session
from app.models.post import Post, PostStatus
from app.models.user import User
from app.services.post_like import create_post_like, delete_post_like

router = APIRouter(prefix="/posts", tags=["posts-likes"])


@router.put(
    "/{post_id}/likes/me",
    status_code=201,
    response_class=Response,
    responses={204: {"description": "Лайк уже установлен"}},
    summary="Поставить лайк на пост",
)
async def put_post_like(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    post: Annotated[Post, Depends(get_readable_post)],
) -> Response:
    if post.status != PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=403,
            detail="Likes are only allowed on published posts",
        )

    created = await create_post_like(session, post.id, user.id)
    return Response(status_code=201 if created else 204)


@router.delete(
    "/{post_id}/likes/me",
    status_code=204,
    summary="Снять свой лайк с поста",
)
async def remove_post_like(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    post: Annotated[Post, Depends(get_readable_post)],
):
    await delete_post_like(session, post.id, user.id)
