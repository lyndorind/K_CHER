"""Налаштування підключення до бази даних зі змінних середовища."""

import os
from pathlib import Path

from sqlalchemy.engine import URL


def _read_password() -> str | None:
    """Пароль береться з файлу (Docker secret) або зі змінної DB_PASSWORD."""
    password_file = os.getenv("DB_PASSWORD_FILE")
    if password_file:
        return Path(password_file).read_text(encoding="utf-8").strip()
    return os.getenv("DB_PASSWORD")


def get_database_url() -> URL | str | None:
    """Повертає URL бази даних або None, якщо базу не налаштовано."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    host = os.getenv("DB_HOST")
    if not host:
        return None

    return URL.create(
        "postgresql+psycopg",
        username=os.getenv("DB_USER", "kcher"),
        password=_read_password(),
        host=host,
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "kcher"),
    )
