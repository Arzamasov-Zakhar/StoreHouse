"""Модуль с таблицей недвижимостей."""
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import func

from src.core.config import HASHER
from src.tables import Base
from src.core.db import CREATED_AT_COLUMN, UPDATED_AT_COLUMN

class Immovables(Base):
    """Модель недвижимости."""

    __tablename__ = "immovable"

    id = sa.Column(  # noqa:  A003
        "id", sa.Integer, primary_key=True, autoincrement=True
    )
    user_id = sa.Column(
        "user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False
    )
    address = sa.Column("address", sa.String(256), nullable=True)
    storehouse_ids = sa.Column(
        "storehouse_ids", sa.ARRAY(sa.Integer), nullable=True, default=None
    )
    title = sa.Column("title", sa.String(64), nullable=False)
    description = sa.Column("description", sa.String(10000), nullable=True)
    created_at = sa.Column(
        "created_at",
        sa.TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at = UPDATED_AT_COLUMN()
