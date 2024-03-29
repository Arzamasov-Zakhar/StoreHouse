"""Модуль с представлениями недвижимостей."""
from typing import Union

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from src.rest.permissions import AuthChecker
from src.rest.service.base import BaseView
from src.utils.cbv import cbv
from starlette.responses import JSONResponse, Response
from starlette import status
from src.rest.models.immovable import ImmovableModel, ResponseImmovableModel
from src.tables import Immovables

router = APIRouter()


@cbv(router)
class ImmovableView(BaseView):
    """Представление для работы с недвижимостью."""

    @router.post(
        "/immovable",
        # dependencies=[Depends(AuthChecker(is_auth=True))],
        responses={400: {}, 201: {}},
    )
    async def immovable_post(
        self, immovable: ImmovableModel = Depends(ImmovableModel.as_form)  # noqa B008
    ):  # noqa ANN201
        """Запрос на создание недвижимости."""
        return await self.create_immovable(immovable)

    async def create_immovable(
        self,
        immovable: Union[ImmovableModel],
    ) -> Response:
        """Создать недвижимость."""
        immovable_data = immovable.dict()
        immovable_data["user_id"] = self.request.user.id
        await Immovables.create(**immovable_data)
        return Response(status_code=status.HTTP_201_CREATED)

    @router.get(
        "/immovables/my",
        dependencies=[Depends(AuthChecker(is_auth=True))],
        response_model=Page[ResponseImmovableModel],
    )
    async def my_dream_list(self) -> dict:
        """Получение списка недвижимостей конкретного пользователя."""
        my_immovables = Immovables.query.where(Immovables.user_id == self.request.user.id).gino.all()

        return my_immovables

    @router.get(
        "/immovable/{immovable_id}",
        dependencies=[Depends(AuthChecker(is_auth=True))],
        response_model=ResponseImmovableModel,
    )
    async def my_dream_list(self, immovable_id: int) -> dict:
        """Получение конкретной недвижимости пользователя."""
        immovable = Immovables.query.where(Immovables.id == immovable_id).gino.first()
        if not immovable:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return immovable
