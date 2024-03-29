"""Модуль с таблицей объектов."""
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import func

from src.core.config import HASHER
from src.tables import Base

class Item(Base):
    """Модель предметов, находящихся в кладовке."""

    __tablename__ = "item"

    id = sa.Column(  # noqa:  A003
        "id", sa.Integer, primary_key=True, autoincrement=True
    )
    user_id = sa.Column(
        "user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False
    )
    storehouse_id = sa.Column(sa.Integer, sa.ForeignKey("storehouse.id"), nullable=False)
    title = sa.Column("title", sa.String(64), nullable=True)
    description = sa.Column("description", sa.String(10000), nullable=True)
    added_at = sa.Column(
        "added_at",
        sa.TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    thrown_out_at = sa.Column("thrown_out_at", sa.TIMESTAMP, nullable=True)
