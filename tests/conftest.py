import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from k_cher.api import app
from k_cher.db import get_db, get_engine, get_session_factory
from k_cher.models import Base

DB_ENV_VARS = (
    "DATABASE_URL",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_PASSWORD_FILE",
)


@pytest.fixture(autouse=True)
def _isolated_db_env(monkeypatch):
    """Тести не залежать від змінних середовища БД і кешів підключення."""
    for name in DB_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    yield
    get_engine.cache_clear()
    get_session_factory.cache_clear()


@pytest.fixture()
def client():
    """Клієнт API з БД SQLite у пам'яті замість PostgreSQL."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
