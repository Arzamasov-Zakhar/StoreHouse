"""Функции загрузки приложения в разных режимах."""
import inspect
from typing import Any

from aiohttp import hdrs
from fastapi import APIRouter
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

import src
from src.core.config import settings
from src.core.container import Container
from src.core.db import async_engine
from src.core.middleware import LoggerMiddleware
from src.rest.middlewares import BasicAuthBackend
from src.rest.views import auth, healthcheck, registration, immovable, storehouse
from src.utils.constants import Tags


def init_container() -> Container:
    """Иницилизация контейнера DI."""
    container = Container(db=async_engine)
    container.init_resources()
    container.check_dependencies()
    packages = set()
    for _, module in inspect.getmembers(src, inspect.ismodule):
        packages.add(module.__name__)
    container.wire(packages=packages)
    return container


def init_routes(app: Any) -> None:
    """Иницаиализация роутов."""
    router = APIRouter()
    router.include_router(healthcheck.router, tags=[Tags.HEALTHCHECK])

    api = APIRouter(prefix="/api")
    api.include_router(auth.router, tags=[Tags.AUTH])
    api.include_router(registration.router, tags=[Tags.REGISTRATION])
    api.include_router(immovable.router, tags=[Tags.IMMOVABLE])
    api.include_router(storehouse.router, tags=[Tags.STOREHOUSE])
    api.include_router(registration.router, tags=[Tags.REGISTRATION])
    router.include_router(api)

    app.include_router(router)


def init_middlewares(app: Any) -> None:
    """Инициализация промежуточных слоев."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.PUBLIC_CORS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=(hdrs.CONTENT_TYPE, hdrs.AUTHORIZATION),
    )
    app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
    app.add_middleware(LoggerMiddleware)
