"""Модуль с таблицами токенов."""
import sqlalchemy as sa

from src.tables import Base


class Blacklist(Base):
    """Модель c заблокированными токенами."""

    __tablename__ = "blacklist"

    id = sa.Column(  # noqa:  A003
        "id", sa.Integer, primary_key=True, autoincrement=True
    )
    jti = sa.Column("jti", sa.String, nullable=False)
