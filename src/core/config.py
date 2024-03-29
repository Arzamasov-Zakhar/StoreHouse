"""Модуль с настройками проекта."""
import logging.config
import sys
from typing import Any, Optional

import argon2
from loguru import logger
from pydantic import validator
from pydantic_settings import BaseSettings

from src.core.logging_config import LOGGINT_CONFIG


class Settings(BaseSettings):
    """Класс настроек."""

    JWT_KEY: str = ""
    ACCESS_LIFETIME: int = 60 * 5
    REFRESH_LIFETIME: int = 60 * 60 * 24
    ENVIRONMENT: str = "dev"
    ALEMBIC_PATH: str = "/etc/src/alembic.ini"
    PROJECT_HOST: str = "http://0.0.0.0:8080"
    FRONT_HOST: str = "http://0.0.0.0:7000"
    PUBLIC_CORS: str = ""

    # RabbitMQ settings
    RABBIT_HOST: str = ""
    RABBIT_PORT: int = 5672
    RABBIT_USERNAME: str = ""
    RABBIT_PASSWORD: str = ""
    RABBIT_VHOST: str = ""
    RABBIT_URL: Optional[str] = None

    @validator("RABBIT_URL")
    def assemble_broker_url(
        cls, v: Optional[str], values: dict[str, Any]
    ) -> str:
        """Получение url для rabbit."""
        if isinstance(v, str):
            return v

        return "amqp://{}:{}@{}:{}/{}".format(
            values.get("RABBIT_USERNAME"),
            values.get("RABBIT_PASSWORD"),
            values.get("RABBIT_HOST"),
            values.get("RABBIT_PORT"),
            values.get("RABBIT_VHOST"),
        )

    EXCHANGE_NAME: str = "src-tasks"

    LEN_IMMOVABLE_TITLE: int = 100
    LEN_STOREHOUSE_TITLE: int = 30
    FILE_SIZE: int = 500


settings = Settings()
HASHER = argon2.PasswordHasher()

logger.add(sys.stdout, backtrace=False, diagnose=False)
# Настройки Gunicorn
logging.config.dictConfig(LOGGINT_CONFIG)
