"""Объекты для работы очередей."""
import json
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Generator, List, Optional, Union

import aio_pika
from dependency_injector.wiring import Provide, inject
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.container import Container
from src.core.rabbitmq import RabbitMQ


class Message(BaseModel):
    """Схема сообщения."""

    id: uuid.UUID  # noqa: A003
    task: str
    args: list = []
    kwargs: dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def info(self) -> str:
        """Форматирование сообщения для логов."""
        return f"{self.task}[{self.id}]"


class Binding(BaseModel):
    """Binding exchange to queue."""

    exchange_name: str
    type: aio_pika.ExchangeType  # noqa: A003
    durable: bool


class TaskHandler:
    """Схема для обработки таска."""

    name: str
    func: Callable

    def __init__(self, name: str, func: Callable) -> None:
        """Инициализация обертки для функций."""
        self.name = name
        self.func = func

        self.exchange_name = settings.EXCHANGE_NAME
        self.exchange_type = aio_pika.ExchangeType.DIRECT
        self.durable = True

    async def delay(self, *args: tuple, **kwargs: dict) -> Any:
        """Метод планирования задачи в очередь."""
        return await self.send_task(self.name, args=args, kwargs=kwargs)

    async def run(self, *args: tuple, **kwargs: dict) -> None:
        """Запуск функции."""
        await self.func(*args, **kwargs)

    async def send_task(
        self,
        task: str,
        *,
        args: Optional[tuple] = None,
        kwargs: Optional[Union[dict, BaseModel]] = None,
        priority: int = 0,
    ) -> None:
        """Формирование и отравка задачи в очередь."""
        message = self._create_message(
            task, args=args, kwargs=kwargs, priority=priority
        )
        await self._publish(message)
        logger.info(
            "task sent", task=task, args=args, kwargs=kwargs, priority=priority
        )

    @classmethod
    def _create_message(  # noqa WPS211
        cls,
        task: str,
        *,
        args: Optional[list] = None,
        kwargs: Optional[Union[dict, BaseModel]] = None,
        delivery_mode: aio_pika.DeliveryMode = aio_pika.DeliveryMode.PERSISTENT,
        priority: Optional[int] = None,
    ) -> aio_pika.Message:
        """Форматирования сообщения для очереди."""
        data = {
            "id": uuid.uuid4(),
            "task": task,
            "args": args or [],
            "kwargs": kwargs or {},
        }
        return aio_pika.Message(
            json.dumps(jsonable_encoder(data)).encode(),
            content_type="application/json",
            delivery_mode=delivery_mode,
            timestamp=datetime.utcnow(),
            priority=priority,
        )

    @inject
    async def _publish(
        self,
        message: aio_pika.Message,
        routing_key: Optional[str] = None,
        rabbitmq: RabbitMQ = Provide[Container.rabbitmq],
    ) -> None:
        """Публикация задачи в очередь."""
        async with rabbitmq.channel_pool.acquire() as channel:
            exchange = await channel.declare_exchange(
                name=self.exchange_name,
                type=self.exchange_type,
                durable=self.durable,
            )

            await exchange.publish(
                message,
                routing_key=routing_key or self.exchange_name,
            )

            logger.info(
                "message published",
                exchange_name=self.exchange_name,
                message_body=message.body,
                **message.info(),
            )


class MessageProcessor:  # noqa: WPS214
    """Процессор обрабатывающий задачи."""

    def __init__(self) -> None:
        """Инициализация процессора."""
        self._processors: dict[str, TaskHandler] = {}

    def task(self, name: str) -> Callable[[Callable], TaskHandler]:
        """Декоратор для регистрации задач."""

        def wrapper(func: Callable) -> TaskHandler:
            """Внутренняя оберка для декоратора."""
            wrapper_obj = TaskHandler(name, func)
            self.register_task(name, wrapper_obj)
            return wrapper_obj

        return wrapper

    def include(self, inner: "MessageProcessor") -> None:
        """Зарегистрировать таски из других процессоров."""
        for task_handler in inner.get_registered_tasks():
            self.register_task(name=task_handler.name, obj=task_handler)

    async def process(self, raw_message: aio_pika.IncomingMessage) -> None:
        """Обработка полученного сообщения."""
        await self.pre_process(raw_message)
        message = await self.parse_message(raw_message)

        if message.task not in self._processors:
            logger.warning(
                f"Received unknown or unregistered task: {message.info}. "
                "Maybe you forgot to register_task it in message_processor. "
                "Task will be dropped",
                error="unknown",
                message=message.json(),
            )
            return
        logger.info(f"Received task: {message.info}")
        logger.info(message.json())

        start_time = time.perf_counter()
        try:
            await self.run_handler(message)
        except Exception:
            logger.exception("Handler raised exception")
        end_time = time.perf_counter()

        logger.info(
            f"Task {message.info} completed in {end_time - start_time:.10f} seconds",
        )

    def register_task(self, name: str, obj: TaskHandler) -> None:
        """Регистрация задачи в обработчике."""
        self._processors[name] = obj

    def get_registered_tasks(self) -> Generator[TaskHandler, None, None]:
        """Генератор загруженных задач."""
        yield from self._processors.values()

    def show_registered_tasks(self) -> None:
        """Показ всех загруженных задач."""
        for task in self.get_registered_tasks():
            logger.info(
                f"\t\tTask [{task.name}] registered"
                f" from {task.func.__module__}.{task.func.__name__}"
            )

    async def pre_process(self, message: aio_pika.IncomingMessage) -> None:
        """Проверка сообщения перед декодингом."""
        if message.content_type != "application/json":
            logger.error("Cannot process not JSON content type")
            raise NotImplementedError

    async def parse_message(
        self, message: aio_pika.IncomingMessage
    ) -> Message:
        """Парсинг полученного сообщения из очереди в объект."""
        try:
            return Message.parse_raw(message.body)
        except Exception as exeption:
            logger.error(f"Got unexpected error: {exeption!r}")
            raise exeption

    async def run_handler(self, message: Message) -> None:
        """Запуск функции из очереди."""
        await self._processors[message.task].run(
            *message.args,
            **message.kwargs,
        )


class Consumer:
    """Обработчик сообщений."""

    exchange_name: str = settings.EXCHANGE_NAME
    exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT
    exclusive: bool = False
    durable: bool = True
    message_processor: MessageProcessor
    queue: aio_pika.Queue

    def __init__(
        self,
        message_processor: MessageProcessor,
        bindings: Optional[List[Binding]] = None,
        prefetch_count: int = 30,
    ) -> None:
        """Инициализация обработчика сообщений."""
        self.message_processor = message_processor
        self.bindings = bindings or []
        self.prefetch_count = prefetch_count

    async def run(self) -> None:
        """Запуск воркера."""
        self.message_processor.show_registered_tasks()
        await self.startup()

    @inject
    async def startup(  # noqa WPS217
        self, rabbitmq: RabbitMQ = Provide[Container.rabbitmq]  # noqa WPS404
    ) -> None:
        """Запуск прослушивания очередей и обработки задач."""
        async with rabbitmq.channel_pool.acquire() as channel:
            await channel.set_qos(prefetch_count=self.prefetch_count)

            exchange = await channel.declare_exchange(
                self.exchange_name,
                self.exchange_type,
                self.durable,
            )

            # Bind queue to default direct exchange
            self.queue = await channel.declare_queue(
                self.exchange_name,
                exclusive=self.exclusive,
                durable=self.durable,
            )
            await self.queue.bind(exchange)

            # Bind other exchanges to this queue
            for binding in self.bindings:
                exchange = await channel.declare_exchange(
                    name=binding.exchange_name,
                    type=binding.type,
                    durable=binding.durable,
                )
                await self.queue.bind(
                    exchange, routing_key=binding.exchange_name
                )

            await self.queue.consume(self.on_message)

    async def on_message(self, message: aio_pika.IncomingMessage) -> None:
        """Функция при получении сообщения из канала."""
        async with message.process():
            return await self.message_processor.process(message)
