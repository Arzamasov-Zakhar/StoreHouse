"""Модуль с таблицей юзера."""
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import func

from src.core.config import HASHER
from src.tables import Base


def password() -> str:
    """Генерация пароля."""
    return HASHER.hash(str(uuid4()))


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"

    id = sa.Column(  # noqa:  A003
        "id", sa.Integer, primary_key=True, autoincrement=True
    )
    username = sa.Column("username", sa.String, nullable=True)
    name = sa.Column("name", sa.String, nullable=True)
    last_name = sa.Column("last_name", sa.String, nullable=True)
    avatar = sa.Column("avatar", sa.String, nullable=True)
    created_at = sa.Column(
        "created_at",
        sa.TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    is_admin = sa.Column("is_admin", sa.Boolean(), default=False)
    is_active = sa.Column("is_active", sa.Boolean(), default=False)
    password = sa.Column("password", sa.String(128), default=password)
    token = sa.Column("token", sa.String)
    email = sa.Column("email", sa.String(128), unique=True)
    immovable_ids = sa.Column(
        "immovable_ids", sa.ARRAY(sa.Integer), nullable=True, default=None
    )
