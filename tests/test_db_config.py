import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

import k_cher.db as db_module
from k_cher.api import app
from k_cher.config import get_database_url
from k_cher.db import get_db, get_engine, init_db
from k_cher.models import Base


def test_returns_none_when_not_configured():
    assert get_database_url() is None


def test_database_url_has_priority(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h/db")
    monkeypatch.setenv("DB_HOST", "ignored")

    assert get_database_url() == "postgresql+psycopg://u:p@h/db"


def test_url_is_built_from_parts(monkeypatch):
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "app")
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "p@ss/word")

    url = get_database_url()

    assert url.drivername == "postgresql+psycopg"
    assert (url.host, url.port, url.database, url.username) == (
        "db",
        5433,
        "app",
        "user",
    )
    assert url.password == "p@ss/word"


def test_password_is_read_from_file(monkeypatch, tmp_path):
    secret = tmp_path / "db_password"
    secret.write_text("from-file\n", encoding="utf-8")
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PASSWORD", "ignored")
    monkeypatch.setenv("DB_PASSWORD_FILE", str(secret))

    assert get_database_url().password == "from-file"


def test_engine_and_session_are_created_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    engine = get_engine()
    session = next(get_db())

    assert engine.dialect.name == "sqlite"
    assert get_engine() is engine
    assert session.execute(text("SELECT 1")).scalar() == 1


def test_get_db_raises_503_when_not_configured():
    with pytest.raises(HTTPException) as error:
        next(get_db())

    assert error.value.status_code == 503


def test_init_db_creates_tables(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    init_db()

    assert inspect(get_engine()).has_table("calculations")


def test_init_db_retries_until_database_is_available(monkeypatch):
    calls = []

    def flaky_create_all(_bind):
        calls.append(1)
        if len(calls) < 3:
            raise OperationalError("CREATE TABLE", {}, Exception("down"))

    monkeypatch.setattr(db_module, "get_engine", lambda: object())
    monkeypatch.setattr(db_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(Base.metadata, "create_all", flaky_create_all)

    init_db(retries=5)

    assert len(calls) == 3


def test_init_db_gives_up_after_all_retries(monkeypatch):
    def failing_create_all(_bind):
        raise OperationalError("CREATE TABLE", {}, Exception("down"))

    monkeypatch.setattr(db_module, "get_engine", lambda: object())
    monkeypatch.setattr(db_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(Base.metadata, "create_all", failing_create_all)

    with pytest.raises(OperationalError):
        init_db(retries=2)


def test_lifespan_initializes_database_when_configured(monkeypatch):
    called = []
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setattr("k_cher.api.init_db", lambda: called.append(True))

    with TestClient(app):
        pass

    assert called == [True]


def test_lifespan_skips_database_when_not_configured(monkeypatch):
    called = []
    monkeypatch.setattr("k_cher.api.init_db", lambda: called.append(True))

    with TestClient(app):
        pass

    assert called == []
