"""Модуль с http исключениями."""
from typing import Any

from fastapi import HTTPException
from starlette import status


class BaseHTTPException(HTTPException):
    """Базовое Исключение."""

    _exception_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, **kwargs: Any) -> None:
        """Инициализация с статусом ошибки."""
        super().__init__(self._exception_code, **kwargs)


class HTTPException403(BaseHTTPException):
    """403 Исключение."""

    _exception_code = status.HTTP_403_FORBIDDEN


class HTTPException404(BaseHTTPException):
    """404 Исключение."""

    _exception_code = status.HTTP_404_NOT_FOUND


class HTTPException400(BaseHTTPException):
    """400 Исключение."""

    _exception_code = status.HTTP_400_BAD_REQUEST
