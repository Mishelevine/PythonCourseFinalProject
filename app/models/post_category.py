from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.post import Post


class PostCategory(Base):
    __tablename__ = "post_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String, unique=True)

    # relationships для доступа к связанным объектам в Python
    posts: Mapped[list["Post"]] = relationship(
        back_populates="category",
        passive_deletes=True,
    )
