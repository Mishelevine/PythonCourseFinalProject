from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_session
from app.models.post_category import PostCategory
from app.schemas.post_category import (
    GetPostCategoryResponse,
    PostCategoryCreate,
    PostCategoryUpdate,
)
from app.services.post_category import (
    CategoryNameAlreadyExistsError,
    delete_post_category,
    get_post_categories,
    update_post_category,
)
from app.services.post_category import (
    create_post_category as create_post_category_db,
)
from app.services.post_category import (
    get_post_category_by_id as get_post_category_db,
)

router = APIRouter(prefix="/post-categories", tags=["post-categories"])


async def get_post_category_by_id(
    post_category_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PostCategory:
    post_category = await get_post_category_db(session, post_category_id)
    if post_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return post_category


@router.get(
    "",
    response_model=list[GetPostCategoryResponse],
    summary="Получение списка категорий постов",
)
async def list_post_categories(
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await get_post_categories(session, offset, limit)


@router.get(
    "/{post_category_id}",
    response_model=GetPostCategoryResponse,
    summary="Получение информации о категории постов",
)
async def get_post_category(
    post_category: Annotated[PostCategory, Depends(get_post_category_by_id)],
):
    return post_category


@router.post(
    "",
    status_code=201,
    response_model=GetPostCategoryResponse,
    dependencies=[Depends(get_current_admin)],
    summary="Создание категории постов",
)
async def create_post_category(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: PostCategoryCreate,
):
    try:
        return await create_post_category_db(session, data.category_name)
    except CategoryNameAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.patch(
    "/{post_category_id}",
    response_model=GetPostCategoryResponse,
    dependencies=[Depends(get_current_admin)],
    summary="Обновление категории постов",
)
async def patch_post_category(
    session: Annotated[AsyncSession, Depends(get_session)],
    post_category: Annotated[PostCategory, Depends(get_post_category_by_id)],
    data: PostCategoryUpdate,
):
    try:
        return await update_post_category(session, post_category, data)
    except CategoryNameAlreadyExistsError as error:
        # 409 - Conflict
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete(
    "/{post_category_id}",
    status_code=204,
    dependencies=[Depends(get_current_admin)],
    summary="Удаление категории постов",
)
async def remove_post_category(
    session: Annotated[AsyncSession, Depends(get_session)],
    post_category: Annotated[PostCategory, Depends(get_post_category_by_id)],
):
    return await delete_post_category(session, post_category)
