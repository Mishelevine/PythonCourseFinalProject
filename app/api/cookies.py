from fastapi import Response

from app.core.config import settings


# Сохраняем refresh token в куки
def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,  # запрет чтения куки из JS
        secure=settings.cookie_secure,  # true - только https
        samesite="lax",  # можно отправлять куки в пределах одного origin
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/auth",
    )


# Удаление refresh token в куки
def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/auth",
    )
