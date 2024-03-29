"""Модуль с моделями хранилищ."""
from pydantic import BaseModel, constr

from src.core.config import settings
from fastapi import Form, File
from typing import List, Optional
# from src.rest.models.images import UploadCloudModel
from src.rest.models.utils import as_form


@as_form
class StoreHouseModel(BaseModel):
    """Модель хранилища."""

    title: constr(max_length=settings.LEN_STOREHOUSE_TITLE) = Form(...)
    description: str = Form(...)
    is_medicinechest: bool = Form(...)
    picture: bool = Form(...)# UploadCloudModel.get_type() = File(...)


class ResponseStoreHouseModel(BaseModel):
    """Модель хранилища для ответа."""

    id: int  # noqa A003
    title: Optional[str]
    description: Optional[str]
    picture: Optional[str]


class StoreHouseListModel(BaseModel):
    """Модель списка хранилищ."""
    ...