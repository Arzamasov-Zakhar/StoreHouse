"""Модуль с таблицей хранищ."""

import sqlalchemy as sa
from sqlalchemy import func

from src.tables import Base

class StoreHouse(Base):
    """Модель хранилища."""

    __tablename__ = "storehouse"

    id = sa.Column(  # noqa:  A003
        "id", sa.Integer, primary_key=True, autoincrement=True
    )
    user_id = sa.Column(
        "user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False
    )
    immovable_id = sa.Column(sa.Integer, sa.ForeignKey("immovable.id"), nullable=False)
    title = sa.Column("title", sa.String(64), nullable=True)
    description = sa.Column("description", sa.String(10000), nullable=True)
    created_at = sa.Column(
        "created_at",
        sa.TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    is_medicinechest = sa.Column("is_medicinechest", sa.Boolean(), nullable=False)
