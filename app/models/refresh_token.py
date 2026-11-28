from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True)

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    # Когда токен использовался для обновления Access
    used_at: Mapped[datetime | None] = mapped_column(DateTime)
    # Когда токен был отозван пользоавтелем
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)

    # foreign keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )
