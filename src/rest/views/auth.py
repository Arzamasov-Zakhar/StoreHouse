"""Модуль с рест авторизацией."""
from fastapi import APIRouter, Depends

from src.rest.models.user import Auth, TokenPair
from src.rest.permissions import AuthChecker
from src.rest.service.base import JWTView
from src.utils.cbv import cbv

router = APIRouter()


@cbv(router)
class TokenObtainPairView(JWTView):
    """Представление для получения пары токенов."""

    # @inject
    @router.post(
        "/token",
        responses={
            401: {"description": "Unauthorized"},
            200: {"model": TokenPair},
        },
    )
    async def user_obtain(self, auth_data: Auth) -> dict:
        """Запрос на получение пары токенов для пользователей."""
        return await self._obtain(auth_data)

    @router.post(
        "/logout",
        dependencies=[Depends(AuthChecker(is_base_auth=True))],
        responses={200: {}},
    )
    async def user_logout(self) -> None:
        """Логаут юзера."""
        return await self.logout()

    @router.post(
        "/token/refresh",
        responses={400: {}},
        response_model=TokenPair,
    )
    async def user_refresh(self) -> dict:
        """Запрос на обновление пары токенов."""
        return await self._refresh()
