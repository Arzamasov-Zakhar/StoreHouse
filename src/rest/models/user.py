"""Модуль с моделями для юзеров."""
from pydantic import BaseModel


class TokenPair(BaseModel):
    """Модель пары access/refresh токенов."""

    access: str
    refresh: str


class Auth(BaseModel):
    """Модель авторизации."""

    email: str
    password: str
