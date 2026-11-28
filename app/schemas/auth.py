from typing import Literal

from password_validator import PasswordValidator
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

# Настройки валидации пароля
password_policy = (
    PasswordValidator()
    .min(8)
    .max(128)
    .has()
    .uppercase()
    .has()
    .lowercase()
    .has()
    .digits()
    .has()
    .symbols()
)


# Регистрация пользователя
class UserRegister(BaseModel):
    login: str = Field(min_length=4, max_length=40)
    password: SecretStr = Field(min_length=8, max_length=128)
    about: str | None = Field(default=None, max_length=1000)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    displayed_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if not password_policy.validate(value.get_secret_value()):
            raise ValueError(
                "Пароль должен содержать строчную и заглавную буквы, "
                "цифру и спецсимвол"
            )
        return value


# Ответ на регистрацию пользователя
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    first_name: str | None
    last_name: str | None
    displayed_name: str
    about: str | None


# Вход пользователя
class UserLogin(BaseModel):
    login: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)


class UserPasswordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: SecretStr = Field(min_length=1, max_length=128)
    new_password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: SecretStr) -> SecretStr:
        if not password_policy.validate(value.get_secret_value()):
            raise ValueError(
                "Пароль должен содержать строчную и заглавную буквы, "
                "цифру и спецсимвол"
            )
        return value


# Ответ с Access Token
class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


# Ответ с Access Token + Refresh Token
class TokenPairResponse(AccessTokenResponse):
    refresh_token: str
