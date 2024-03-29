"""Модуль с моделями недвижимостей."""
from pydantic import BaseModel, constr

from src.core.config import settings
from fastapi import Form
from typing import List, Optional
from src.rest.models.utils import as_form


@as_form
class ImmovableModel(BaseModel):
    """Модель недвижимости."""

    title: constr(max_length=settings.LEN_IMMOVABLE_TITLE) = Form(...)
    address: str = Form(..., max_length=256)
    description: str = Form(...)
    location: str = Form(...)


class ResponseImmovableModel(BaseModel):
    """Модель недвижимости для ответа."""

    id: int  # noqa A003
    title: Optional[str]
    description: Optional[str]
    address: Optional[str]


class ImmovableListModel(BaseModel):
    """Модель списка недвижимостей."""
    ...
