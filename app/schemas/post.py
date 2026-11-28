from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.post import PostStatus


# Пост для списка без полного текста
class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: PostStatus
    user_id: int
    category_id: int | None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    likes_count: int = 0
    is_liked: bool = False


# Текст поста
class PostResponse(PostListItem):
    content_text: str


class PostCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    content_text: str = Field(min_length=1)
    category_id: int | None = Field(default=None, gt=0)
    status: PostStatus = PostStatus.DRAFT


class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content_text: str | None = Field(default=None, min_length=1)
    category_id: int | None = Field(default=None, gt=0)
    status: PostStatus | None = None

    # Эти поля можно пропустить, но нельзя явно передать null
    @field_validator("title", "content_text", "status")
    @classmethod
    def validate_required_fields(
        cls, value: str | PostStatus | None
    ) -> str | PostStatus:
        if value is None:
            raise ValueError("Поле не может быть пустым")
        return value
