from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_text: str = Field(min_length=1, max_length=5000)

    @field_validator("content_text")
    @classmethod
    def validate_content_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Комментарий не может состоять из пробелов")
        return value


# При изменении комментария разрешено передавать только текст
class PostCommentUpdate(PostCommentCreate):
    pass


class PostCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    user_id: int
    content_text: str
    created_at: datetime
    updated_at: datetime
