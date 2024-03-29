"""Модуль с моделями регистрации."""
from pydantic import BaseModel, constr


class RegistrationModel(BaseModel):
    """Модель регистрации."""

    email: str
    password: constr(min_length=8, max_length=50)
