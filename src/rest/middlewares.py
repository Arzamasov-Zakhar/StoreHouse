"""Модуль с middleware."""
import re
from contextvars import ContextVar
from datetime import datetime

import jwt
import sqlalchemy as sa
from fastapi import Request
from jwt import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from starlette import status
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.responses import JSONResponse

from src.core.config import settings
from src.tables.user import User as UserTable
from src.utils.db import DbRequest
from src.utils.exceptions.jwt import BlacklistedError
from src.utils.token import read_jwt_token
from src.utils.types import User

REST_PUBLIC_URL_PATTERN = re.compile(r"^(/v\d+|/latest)?/api/(?!admin).*")
REST_ADMIN_URL_PATTERN = re.compile(r"^(/v\d+|/latest)?/api/admin.*")

request_var: ContextVar = ContextVar("request")


class Handler:
    """Базовый Класс для работы с заголовками."""

    @classmethod
    def unauthorized_response(cls) -> JSONResponse:
        """Получить неавторизованный ответ."""
        return JSONResponse(
            {"errors": [{"message": "Unauthorized"}]},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @classmethod
    async def verify_token(
        cls, request: Request, table: sa.table, token: str = None
    ) -> dict[str, any] | None:
        """Проверка JWT токена.

        Загрузка его в payload, если он представлен в заголовках запроса.
         Иначе вернуть None.
        """
        # TODO блокировать протухший токен
        try:
            payload = await read_jwt_token(
                request, token=token, key=settings.JWT_KEY
            )
        except (
            jwt.DecodeError,
            BlacklistedError,
            ExpiredSignatureError,
        ) as error:
            raise PermissionError from error

        user_id = int(payload.get("id"))
        if not user_id:
            raise PermissionError

        query = select(UserTable).where(UserTable.id == user_id)
        user = await DbRequest.scalar(query)
        if not user:
            raise PermissionError

        return payload  # noqa R504

    @classmethod
    async def authorize_user(
        cls, request: Request, token: str = None
    ) -> UserTable:
        """Авторизовать пользователя в запрос."""
        payload = await cls.verify_token(request, UserTable, token)
        assert payload is not None

        user_id = int(payload.get("id"))
        expires = payload.get("exp")

        if not user_id or not expires or expires <= datetime.utcnow():
            return cls.unauthorized_response()

        query = select(UserTable).where(
            sa.and_(UserTable.id == user_id, UserTable.is_active)
        )
        app_user: UserTable = await DbRequest.scalar(query)
        if not app_user:
            raise NoResultFound

        return app_user


class UserAuthHandler(Handler):
    """Класс для работы с заголовками пользователя."""

    async def __call__(self, request: Request) -> None:
        """Проверить токен доступа пользователя в заголовке.

        Назначить пользователя для запроса.
         Выдает ошибку 401, если предоставлен неверный токен доступа
          или пользователь не может быть найденный.
        """
        if self.in_exclude(request.url.path, request):
            return  # noqa:  R502
        try:
            return User(await self.authorize_user(request))
        except AssertionError:
            return  # noqa:  R502
        except PermissionError:
            raise AuthenticationError("Invalid basic auth credentials")

    @classmethod
    def in_exclude(cls, url: str, request: Request) -> bool:
        """Метод проверки пути."""
        public = not re.match(REST_PUBLIC_URL_PATTERN, url)
        public |= url in (request.app.url_path_for("user_refresh"),)
        return public


class BasicAuthBackend(AuthenticationBackend):
    """Базовая аутентификация бэкенда."""

    handlers = (UserAuthHandler(),)

    async def authenticate(self, request: Request) -> tuple:
        """Authenticate."""
        for handle in self.handlers:
            user = await handle(request)
            if user:
                break

        scope = "authenticated" if user else "not_authenticated"
        return AuthCredentials([scope]), user
