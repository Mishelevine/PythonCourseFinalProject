from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_path: Path = Path("data/app.db")

    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cookie_secure: bool = True

    # Настстройки чтения переменных из .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
