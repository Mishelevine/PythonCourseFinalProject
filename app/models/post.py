from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.post_category import PostCategory
    from app.models.user import User


# Статусы постов
class PostStatus(StrEnum):
    PUBLISHED = "published"
    DRAFT = "draft"


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    content_text: Mapped[str] = mapped_column(Text)

    status: Mapped[PostStatus] = mapped_column(
        Enum(
            PostStatus,
            values_callable=lambda statuses: [
                status.value for status in statuses
            ],
            create_constraint=True,
            name="post_status",
        ),
        default=PostStatus.DRAFT,
        server_default=PostStatus.DRAFT.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    # foreign keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        # SET NULL - если категория будет удалена, установим Null
        ForeignKey("post_category.id", ondelete="SET NULL"),
        index=True,
    )

    # relationships для доступа к связанным объектам в Python
    user: Mapped["User"] = relationship(
        back_populates="posts",
    )
    category: Mapped["PostCategory | None"] = relationship(
        back_populates="posts",
    )
