"""Модуль с фикстурами."""
import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic.command import upgrade
from alembic.config import Config
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient
from yarl import URL

from src.core.config import settings
from src.core.db import async_session
from src.utils.common import get_database_url
from tests.utils import get_tmp_database


@pytest.fixture(scope="session")
def monkeypatch_session() -> MonkeyPatch:
    """Инициализация monkeypatch."""
    patch = MonkeyPatch()
    yield patch
    patch.undo()


@pytest.fixture()
def app(monkeypatch_session: MonkeyPatch, db: str) -> FastAPI:  # noqa PT022
    """Инициализация приложения."""
    from src.app import init_app

    yield init_app()


@pytest.fixture(autouse=True, scope="session")
def db(
    migrated_postgres_template: str, monkeypatch_session: MonkeyPatch
) -> str:
    """Инициализация подключения к бд."""
    template_db = URL(migrated_postgres_template).name
    with get_tmp_database(template=template_db) as tmp_url:
        monkeypatch_session.setenv("DB_NAME", URL(tmp_url).raw_name)
        yield tmp_url


@pytest.fixture(scope="session")
def migrated_postgres_template(
    monkeypatch_session: MonkeyPatch,
) -> Generator[str, None, None]:
    """Создание шаблона базы с применением миграций."""
    with get_tmp_database() as tmp_url:
        alembic_config = Config(file_=settings.ALEMBIC_PATH)
        alembic_config.set_main_option("sqlalchemy.url", tmp_url)
        monkeypatch_session.setenv("DB_NAME", URL(tmp_url).raw_name)
        upgrade(alembic_config, "head")
        yield tmp_url


@pytest.fixture()
def test_client(app: FastAPI) -> TestClient:
    """Получение тестового клиента для отправки запросов."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    """Получение ивентлупа."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop


@pytest.fixture(autouse=True, scope="session")
async def engine(db: str) -> None:
    """Привязанный к мигрированной базе данных SQLAlchemy engine."""
    async_session.kw["bind"] = create_async_engine(
        get_database_url(sync=False)
    )
    yield
    await async_session.kw["bind"].dispose()
