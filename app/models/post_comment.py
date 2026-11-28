from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.post import Post


class PostComment(Base):
    __tablename__ = "post_comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_text: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    # foreign keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"),
        index=True,
    )

    # relationships для доступа к связанным объектам в Python
    post: Mapped["Post"] = relationship(
        back_populates="comments",
    )
