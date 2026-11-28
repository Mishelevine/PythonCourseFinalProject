from pydantic import BaseModel, ConfigDict, Field, field_validator


# Получение информации о пользователе
class GetUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    first_name: str | None
    last_name: str | None
    displayed_name: str
    about: str | None


# Обновление информации о пользователе
class UserUpdate(BaseModel):
    # Запрещаем передавать поля, не объявленные в схеме
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    displayed_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    about: str | None = Field(default=None, max_length=1000)

    @field_validator("displayed_name")
    @classmethod
    def validate_displayed_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Имя профиля не может быть пустым")
        return value
