from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_optional_current_user,
    get_session,
)
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.schemas.post import PostCreate, PostListItem, PostResponse, PostUpdate
from app.services.post import (
    CategoryNotFoundError,
    delete_post,
    get_my_posts,
    get_posts,
    update_post,
)
from app.services.post import create_post as create_post_db
from app.services.post import get_post_by_id as get_post_db

router = APIRouter(prefix="/posts", tags=["posts"])


# Получить пост по id
async def get_post_by_id(
    post_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Post:
    post = await get_post_db(session, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def get_readable_post(
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    post: Annotated[Post, Depends(get_post_by_id)],
) -> Post:
    # Чужие черновики скрываем, администратор может их просматривать
    if post.status == PostStatus.DRAFT and (
        current_user is None
        or (
            current_user.id != post.user_id
            and current_user.user_role != UserRole.ADMIN
        )
    ):
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def get_editable_post(
    current_user: Annotated[User, Depends(get_current_user)],
    post: Annotated[Post, Depends(get_post_by_id)],
) -> Post:
    # Редактировать пост может только автор
    if current_user.id != post.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return post


async def get_deletable_post(
    current_user: Annotated[User, Depends(get_current_user)],
    post: Annotated[Post, Depends(get_post_by_id)],
) -> Post:
    # Удалить пост может автор или администратор
    if (
        current_user.id != post.user_id
        and current_user.user_role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return post


@router.get(
    "",
    response_model=list[PostListItem],
    summary="Получение списка опубликованных постов",
)
async def list_posts(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[int | None, Query(gt=0)] = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await get_posts(session, offset, limit, user_id, category_id)


@router.get(
    "/me",
    response_model=list[PostListItem],
    summary="Получение своих постов, включая черновики",
)
async def list_my_posts(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    status: Annotated[PostStatus | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await get_my_posts(session, user.id, offset, limit, status)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Получение информации о посте",
)
async def get_post(
    post: Annotated[Post, Depends(get_readable_post)],
):
    return post


@router.post(
    "",
    status_code=201,
    response_model=PostResponse,
    summary="Создание поста",
)
async def create_post(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    data: PostCreate,
):
    try:
        return await create_post_db(session, user.id, data)
    except CategoryNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
    summary="Частичное обновление поста",
)
async def patch_post(
    session: Annotated[AsyncSession, Depends(get_session)],
    post: Annotated[Post, Depends(get_editable_post)],
    data: PostUpdate,
):
    try:
        return await update_post(session, post, data)
    except CategoryNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete(
    "/{post_id}",
    status_code=204,
    summary="Удаление поста",
)
async def remove_post(
    session: Annotated[AsyncSession, Depends(get_session)],
    post: Annotated[Post, Depends(get_deletable_post)],
):
    return await delete_post(session, post)
