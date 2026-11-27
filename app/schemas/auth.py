from pydantic import BaseModel, ConfigDict, Field


# Регистрация пользователя
class UserRegister(BaseModel):
    login: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=8, max_length=128)
    displayed_name: str = Field(min_length=1, max_length=100)
    about: str | None = Field(default=None, max_length=1000)


# Ответ на регистрацию пользователя
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    displayed_name: str
    about: str | None
