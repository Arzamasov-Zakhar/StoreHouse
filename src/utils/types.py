"""Модуль с типами проекта."""
from typing import Any, TypeVar

from src.tables import User as UserTable

_Wrapped = TypeVar("_Wrapped")


class BaseType:
    """Базовый тип."""

    instance: _Wrapped

    def __init__(self, instance: _Wrapped) -> None:
        """Добавление юзера в instance."""
        self.instance = instance

    def __getattr__(self, item: str) -> Any:
        """Проксирование обращения к атрибуту."""
        return getattr(self.instance, item)


class User(BaseType):
    """Класс для типизации пользователя."""

    instance: UserTable
