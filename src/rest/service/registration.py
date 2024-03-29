"""Сервис для работы с регистрацией."""
from typing import Any

from dependency_injector.wiring import inject

from src.core.config import HASHER
from src.rest.repository.registration import create_user, get_existing_user
from src.utils.exceptions.repository import RegistrationException


class RegistrationService:
    """Сервис регистрации пользователя."""

    def __init__(self, db: Any) -> None:
        self.db = db

    @inject
    async def registration_user(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> int:  # noqa:  R504
        """Регистрация пользователя."""
        email = kwargs["reg_data"].email.lower()
        password = HASHER.hash(kwargs["reg_data"].password)

        check_user = await get_existing_user(email)
        if check_user:
            error = "Registration error"
            raise RegistrationException(error)

        return await create_user(email, password)
