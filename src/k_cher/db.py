"""Підключення до бази даних (SQLAlchemy)."""

import time
from collections.abc import Iterator
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from k_cher.config import get_database_url
from k_cher.models import Base


@lru_cache
def get_engine() -> Engine:
    url = get_database_url()
    if url is None:
        raise RuntimeError(
            "Базу даних не налаштовано: задайте DB_HOST або DATABASE_URL"
        )
    return create_engine(url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Залежність FastAPI: сесія БД на час одного запиту."""
    try:
        factory = get_session_factory()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    with factory() as session:
        yield session


def init_db(retries: int = 30, delay: float = 1.0) -> None:
    """Створює таблиці; чекає, поки СУБД почне приймати з'єднання."""
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(get_engine())
            return
        except OperationalError:
            if attempt == retries:
                raise
            time.sleep(delay)
