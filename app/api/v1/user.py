from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.models.user import User, UserRole
from app.schemas.user import GetUserResponse, UserUpdate
from app.services.user import (
    delete_user,
    get_users,
    update_user,
)
from app.services.user import (
    get_user_by_id as get_user_db,
)

router = APIRouter(prefix="/user", tags=["user"])


# Получить пользователя по id
async def get_user_by_id(
    user_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    user = await get_user_db(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Проверить доступ к управлению пользователем
async def get_editable_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user: Annotated[User, Depends(get_user_by_id)],
) -> User:
    if current_user.id != user.id and current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    return user


@router.get(
    "",
    response_model=list[GetUserResponse],
    summary="Получение списка пользователей",
)
async def list_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await get_users(session, offset, limit)


@router.get(
    "/{user_id}",
    response_model=GetUserResponse,
    summary="Получение информации о пользователе",
)
async def get_user(
    user: Annotated[User, Depends(get_user_by_id)],
):
    return user


@router.patch(
    "/{user_id}",
    response_model=GetUserResponse,
    summary="Частичное обновление профиля пользователя",
)
async def patch_user(
    data: UserUpdate,
    user: Annotated[User, Depends(get_editable_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await update_user(session, user, data)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Удаление пользователя",
)
async def remove_user(
    user: Annotated[User, Depends(get_editable_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await delete_user(session, user)
