"""Контейнер зависимостей проекта."""
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core import config
from src.core.rabbitmq import RabbitMQ
from src.rest.service.registration import RegistrationService


class Container(containers.DeclarativeContainer):
    """Основной контейнер с зависимостями."""

    # TODO: Если attribute error править тут
    wiring_config = containers.WiringConfiguration(
        modules=["src.rest.views.registration"]
    )

    db = providers.Dependency(instance_of=AsyncEngine)

    rabbitmq = providers.Singleton(
        RabbitMQ,
        rabbit_url=config.settings.RABBIT_URL,
    )
    registration_service = providers.Factory(RegistrationService, db=db)
