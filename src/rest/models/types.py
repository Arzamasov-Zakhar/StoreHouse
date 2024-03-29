"""Модуль с собственными типами."""
from __future__ import annotations

import re
from typing import Any, Callable, Generator, Iterable, Type

from starlette.datastructures import UploadFile

TG_URL_PATTERN = (
    r"(https:\/\/|https:\/\/t\.me\/|t\.me\/|@|)(?P<login>[a-z0-9_+]{5,32}).*"
)
TG_URL_REGEX = re.compile(TG_URL_PATTERN)


class UploadFileOrLink(UploadFile):
    """Тип для загрузки файла побитово или через ссылку."""

    validator = lambda value: value  # noqa E731

    def __new__(
        cls,
        *args: tuple,
        validator: Callable = None,
        **kwargs: dict,
    ) -> type:
        """Создание нового объекта."""
        copy = type("CopyCls", cls.__bases__, dict(cls.__dict__))
        if validator:
            copy.validator = validator
        return copy
