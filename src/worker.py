"""Файл для запуска воркера."""
import asyncio

from aio_pika import ExchangeType
from loguru import logger

from src.core.config import settings
from src.core.consumer import Binding, Consumer
from src.core.db import async_engine
from src.tasks import message_processor
from src.utils.bootstrap import init_container

aggregator_consumer = Consumer(
    message_processor,
    bindings=[
        Binding(
            exchange_name=settings.EXCHANGE_NAME,
            type=ExchangeType.DIRECT,
            durable=True,
        ),
    ],
)


async def main() -> None:
    """Запуск воркера."""
    logger.info("Task daemon starting...")
    container = init_container()
    logger.info("DI Container initialized")
    await container.rabbitmq().connect()
    logger.info("RabbitMQ connected")
    await asyncio.ensure_future(aggregator_consumer.run(), loop=loop)
    logger.info("Task daemon ready!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(), loop=loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(async_engine.pop_bind().close())
        loop.close()
    finally:
        logger.info("Task daemon stopped. Bye!")
