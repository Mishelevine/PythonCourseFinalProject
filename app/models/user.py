from enum import StrEnum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


# Роли пользователей
class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


# Можель пользователя
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    login: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)

    displayed_name: Mapped[str] = mapped_column(String)
    about: Mapped[str | None] = mapped_column(String)

    # Роль ползователя
    user_role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda roles: [role.value for role in roles],
            create_constraint=True,  # создать ограничение в БД
            name="user_role",
        ),
        default=UserRole.USER,  # значение по умолчанию в ORM
        server_default=UserRole.USER.value,  # значение по умолчанию в БД
    )
