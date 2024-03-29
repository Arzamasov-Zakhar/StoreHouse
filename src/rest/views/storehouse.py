"""Модуль с представлениями хранилищ."""
from typing import Union

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from src.rest.models.storehouse import StoreHouseModel, ResponseStoreHouseModel
from src.rest.permissions import AuthChecker
from src.rest.service.base import BaseView
from src.utils.cbv import cbv
from starlette.responses import JSONResponse, Response
from starlette import status
from src.rest.models.immovable import ResponseImmovableModel
from src.tables import StoreHouse, Immovables

router = APIRouter()


@cbv(router)
class StoreHouseView(BaseView):
    """Представление для работы с хранилищами."""

    @router.post(
        "{immovable_id}/storehouse",
        dependencies=[Depends(AuthChecker(is_auth=True))],
        responses={400: {}, 201: {}},
    )
    async def storehouse_post(
        self, immovable_id: int, storehouse: StoreHouseModel = Depends(StoreHouseModel.as_form),   # noqa B008
    ):  # noqa ANN201
        """Запрос на создание недвижимости."""
        return await self.create_storehouse(immovable_id, storehouse)

    async def create_storehouse(
        self,
        immovable_id: int,
        storehouse: Union[StoreHouseModel],
    ) -> Response:
        """Создать хранилище."""
        immovable = await Immovables.get(immovable_id)
        if not immovable:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        storehouse_data = storehouse.dict()
        storehouse_data["user_id"] = self.request.user.id
        storehouse_data["immovable_id"] = immovable_id
        await StoreHouse.create(**storehouse_data)
        return Response(status_code=status.HTTP_201_CREATED)

    @router.get(
        "{immovable_id}/storehouses",
        dependencies=[Depends(AuthChecker(is_auth=True))],
        response_model=Page[ResponseImmovableModel],
    )
    async def my_dream_list(self, immovable_id: int) -> dict:
        """Получение списка хранилищ конкретной недвижимости."""
        immovable = await Immovables.get(immovable_id)
        if not immovable:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        storehouses = StoreHouse.query.where(StoreHouse.immovable_id == immovable_id).gino.all()

        return storehouses

    @router.get(
        "/storehouses/{storehouse_id}",
        dependencies=[Depends(AuthChecker(is_auth=True))],
        response_model=ResponseStoreHouseModel,
    )
    async def my_dream_list(self, storehouse_id: int) -> dict:
        """Получение конкретного хранилища пользователя."""
        storehouse = StoreHouse.query.where(StoreHouse.id == storehouse_id).gino.first()
        if not storehouse:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return storehouse
