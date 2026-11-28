from pydantic import BaseModel, ConfigDict, Field, field_validator


class GetPostCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_name: str


class PostCategoryCreate(BaseModel):
    category_name: str = Field(min_length=1, max_length=30)


class PostCategoryUpdate(BaseModel):
    # Запрещаем передавать поля, не объявленные в схеме
    model_config = ConfigDict(extra="forbid")

    category_name: str | None = Field(
        default=None, min_length=1, max_length=30
    )

    @field_validator("category_name")
    @classmethod
    def validate_category_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Название категории не может быть пустым")
        return value
