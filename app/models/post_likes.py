from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.post import Post


class PostLike(Base):
    __tablename__ = "post_like"

    # Ограничиваем уникальность
    # 1 человек может поставить только 1 лайк на пост
    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_post_like_post_user",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
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
        back_populates="likes",
    )
