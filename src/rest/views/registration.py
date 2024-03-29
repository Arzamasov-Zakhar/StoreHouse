"""Модуль для регистрации."""
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.core.container import Container
from src.rest.models.auth import RegistrationModel
from src.rest.service.base import BaseView
from src.rest.service.registration import RegistrationService
from src.utils.cbv import cbv

router = APIRouter()


@cbv(router)
class Registration(BaseView):
    """Представление для работы с регистрацией."""

    @router.post("/registration", responses={200: {}})
    @inject
    async def register(
        self,
        reg_data: RegistrationModel,
        registration_x: RegistrationService = Depends(
            Provide[Container.registration_service]
        ),
    ) -> Response:
        """Регистрация пользователя."""
        await registration_x.registration_user(reg_data=reg_data)
        # TODO Тут можно реализовать сервис отправку подтверждения регистрации по email.
        return Response(status_code=status.HTTP_200_OK)
