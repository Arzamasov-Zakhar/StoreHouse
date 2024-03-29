"""Модуль с настройками базы."""
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import func

from src.utils.common import get_database_url

metadata = sa.MetaData()

async_engine = create_async_engine(
    get_database_url(sync=False),
    connect_args={"server_settings": {"jit": "off"}},
)

async_session = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

CREATED_AT_COLUMN = lambda: sa.Column(  # noqa E731
    "created_at", sa.TIMESTAMP, server_default=func.now(tz=True)
)

UPDATED_AT_COLUMN = lambda: sa.Column(  # noqa E731
    "updated_at",
    sa.TIMESTAMP,
    server_default=func.now(tz=True),
    server_onupdate=func.now(tz=True),
    default=func.now(tz=True),
    onupdate=func.now(tz=True),
)
