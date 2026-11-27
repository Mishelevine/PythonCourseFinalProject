from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

DATABASE_PATH = settings.db_path
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Движок для управления подключениями к БД
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Фабрика для создания новых сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# Базовый ORM класс
class Base(DeclarativeBase):
    pass