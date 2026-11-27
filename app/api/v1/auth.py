from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.auth import UserRegister, UserResponse
from app.services.auth import (
    LoginAlreadyExistsError,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Регистрация пользователя
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201, # 201 - Created
)
async def register(
    data: UserRegister,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        return await register_user(session, data)
    # Логин уже занят
    except LoginAlreadyExistsError as error:
        raise HTTPException(
            status_code=409, # 409 - Conflict
            detail=str(error),
        ) from error