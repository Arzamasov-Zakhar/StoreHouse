"""Модуль с константами приложения."""
from enum import Enum


class Tags(str, Enum):
    """Тэги приложения."""

    HEALTHCHECK = "healthcheck"
    REGISTRATION = "registration"
    AUTH = "auth"
    IMMOVABLE = "immovable"
    STOREHOUSE = "storehouse"
