"""Модуль с разрешениями для рест запросов."""
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request


class AuthChecker:
    """Проверяет разрешения для рест запросов."""

    def __init__(
        self,
        is_base_auth: bool = False,
        is_auth: bool = False,
    ) -> None:
        """Конструктор класса."""
        self.is_base_auth = is_base_auth
        self.is_auth = is_auth

    def __call__(self, request: Request) -> None:
        """Реализует вызов экземпляра."""
        self.base_check_auth(request)
        self.check_auth(request)

    def base_check_auth(self, request: Request) -> None:
        """Проверка юзера без статуса."""
        if self.is_base_auth and not getattr(request.user, "instance", None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found.",
            )

    def check_auth(self, request: Request) -> None:
        """Проверка юзера."""
        if self.is_auth and not getattr(request.user, "instance", None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found.",
            )
        if self.is_auth and not request.user.instance.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
