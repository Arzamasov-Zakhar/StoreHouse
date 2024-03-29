"""Модуль для работы с токенами."""
from datetime import datetime

import jwt
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request
from jwt import PyJWTError
from starlette import status
from starlette.responses import Response

from src.core.config import settings
from src.rest.models.user import Auth
from src.rest.repository.auth import (
    ban_token,
    get_active_user_by_creds,
    get_active_user_by_id,
)
from src.tables.user import User
from src.utils.exceptions.jwt import BlacklistedError, TokenGoneOffError
from src.utils.token import (
    check_token_blacklist,
    create_token_pair,
    jwt_decode,
)


class BaseView:
    """Базовый класс представления."""

    request: Request
    response: Response


class JWTView(BaseView):  # noqa  WPS214, WPS338
    """Базовое представление для выдачи и бана токенов."""

    async def get_refresh_payload(self) -> dict:
        """Получить payload из refresh токена."""
        token = self.request.cookies.get("refresh", "")
        payload = await self.read_token(token)
        if not await self.validate_token(payload):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return payload

    async def read_token(self, token: str) -> dict:
        """Прочитать данные из токена."""
        try:
            payload = jwt_decode(token, key=settings.JWT_KEY, verify=False)

            active_user = await get_active_user_by_id(payload["id"])
            if not active_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            jwt.decode(
                token,
                key=settings.JWT_KEY,
                verify=bool(settings.JWT_KEY),
                algorithms="HS256",
            )
        except PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token",
            )
        return {**payload, "token": token}

    async def validate_token(self, payload: dict) -> bool:
        """Провалидировать токен."""
        try:
            if payload["exp"] < datetime.utcnow():
                raise TokenGoneOffError
            exist = await check_token_blacklist(
                self.request.app, payload["jti"]
            )
            if exist:
                raise BlacklistedError
        except (TokenGoneOffError, BlacklistedError):
            return False

        return True

    async def get_pair_token_response(
        self, active_user: User, refresh: bool = False
    ) -> dict:
        """Получить ответ с токенами."""
        access_token, refresh_token = create_token_pair(active_user)
        self.response.set_cookie(
            "refresh",
            refresh_token,
            httponly=True,
            secure="https" in settings.FRONT_HOST,
            samesite="none" if "https" in settings.FRONT_HOST else None,
        )
        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    async def _obtain(
        self, auth_data: Auth, admin: bool = False
    ) -> dict | None:
        """Запрос на получение пары токенов."""
        try:
            active_user = await get_active_user_by_creds(
                auth_data.email.lower(), auth_data.password, admin
            )
        except VerifyMismatchError:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)

        return await self.get_pair_token_response(active_user)

    async def logout(self) -> None:
        """Запрос на логаут."""
        payload = await self.get_refresh_payload()

        await ban_token(payload.get("jti", ""))
        await ban_token(payload.get("access_jti", ""))

    async def _refresh(self) -> dict:
        """Запрос на обновление пары токенов."""
        payload = await self.get_refresh_payload()
        return await self.refresh_token(payload)

    async def refresh_token(self, payload: dict) -> dict:
        """Обновить пару токенов."""
        await self.ban_token(payload["jti"])
        await self.ban_token(payload["access_jti"])
        active_user = await get_active_user_by_id(payload["id"])
        if not active_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return await self.get_pair_token_response(active_user, refresh=True)
