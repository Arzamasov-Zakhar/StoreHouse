"""Модуль работы с RabbitMQ."""
from typing import Optional

import aio_pika


class RabbitMQClientBaseError(Exception):
    """Базовое исключение для модуля."""


class NotConnectedError(RabbitMQClientBaseError):
    """Ошибка при отсутствующем подключении к RabbitMQ."""


class RabbitMQ:
    """Клиент для RabbitMQ."""

    rabbit_url: str

    def __init__(self, rabbit_url: str, channel_max_size: int = 3) -> None:
        """Инициализация подключения к RabbitMQ."""
        self.rabbit_url = rabbit_url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel_pool: aio_pika.pool.Pool = aio_pika.pool.Pool(
            self._get_new_channel, max_size=channel_max_size
        )

    def is_connected(self) -> bool:
        """Проверка подключения к RabbitMQ."""
        return self.connection is not None

    async def connect(self) -> None:
        """Подключение к RabbitMQ."""
        self.connection = await aio_pika.connect_robust(self.rabbit_url)

    async def disconnect(self) -> None:
        """Отключение от RabbitMQ."""
        if self.is_connected():
            await self.channel_pool.close()
            await self.connection.close()

    async def _get_new_channel(self) -> aio_pika.Channel:
        """Получение канала для работы с RabbitMQ."""
        if self.is_connected():
            return await self.connection.channel()

        raise NotConnectedError(
            "RabbitMQ not connected. Maybe, you forgot to call `connect()` method"
        )
