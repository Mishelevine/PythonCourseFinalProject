from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cookies import clear_refresh_cookie, set_refresh_cookie
from app.api.deps import get_session
from app.core.security import create_access_token
from app.schemas.auth import (
    AccessTokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import (
    IncorrectLoginOrPassword,
    InvalidRefreshTokenError,
    LoginAlreadyExistsError,
    get_tokens,
    login_user,
    refresh_tokens,
    register_user,
    revoke_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# Регистрация пользователя
@router.post(
    "/register",
    response_model=UserResponse,
    summary="Регистрация нового пользователя",
    status_code=201,  # 201 - Created
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
            status_code=409,  # 409 - Conflict
            detail=str(error),
        ) from error


# Вход пользователя
@router.post("/login", summary="Вход в систему", status_code=200)
async def login(
    data: UserLogin,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        user = await login_user(session, data)
    # Неверные данные для входа
    except IncorrectLoginOrPassword as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    # Получение токенов при успешной регистрации
    tokens = await get_tokens(session, user.id)

    set_refresh_cookie(response, tokens.refresh_token)

    # Возвращаем access token
    return AccessTokenResponse(access_token=tokens.access_token)


# Выход, отзыв текущего refresh token и удаление cookie
@router.post(
    "/logout", summary="Выход из системы", status_code=204
)  # 204 - тело отсутствует
async def logout(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    if refresh_token is not None:
        await revoke_refresh_token(session, refresh_token)

    clear_refresh_cookie(response)


# Обновление токенов
@router.post(
    "/refresh",
    summary="Обновление токенов",
    description="Для работы нужен куки с refresh token",
    response_model=AccessTokenResponse,
)
async def refresh(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    refresh_token: Annotated[
        str | None, Cookie()
    ] = None,  # получаем refresh из cookie
):
    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is missing",
        )

    try:
        tokens = await refresh_tokens(session, refresh_token)
    except InvalidRefreshTokenError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    set_refresh_cookie(response, tokens.refresh_token)

    return AccessTokenResponse(
        access_token=tokens.access_token,
    )


# Запрос для получения Access токена из формы 
# в SwaggerUI c OAuth2PasswordRequestForm
@router.post(
    "/token",
    summary="Получение access token по логину и паролю",
    response_model=AccessTokenResponse,
)
async def token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        data = UserLogin(
            login=form.username,
            password=form.password,
        )
        user = await login_user(session, data)

    except (IncorrectLoginOrPassword, ValidationError) as error:
        raise HTTPException(
            status_code=401,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return AccessTokenResponse(
        access_token=create_access_token(user.id),
    )
