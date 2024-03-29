"""Модель лекарств."""
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import func

from src.core.config import HASHER
from src.tables import Base


class Medicine(Base):
    """Модель лекарств, находящихся в аптечке."""

    __tablename__ = "medicine"

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
    expiration_date = sa.Column("expiration_date", sa.TIMESTAMP, nullable=False)
    start_date = sa.Column("start_date", sa.TIMESTAMP, nullable=True)
    recipe = sa.Column("recipe", sa.String(10000), nullable=True)
