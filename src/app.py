"""Главный модуль приложения."""
from fastapi import FastAPI

from src.core.config import settings
from src.utils.bootstrap import init_container, init_middlewares, init_routes


def init_app() -> FastAPI:
    """Инициализация приложения."""
    app = FastAPI()
    app.container = init_container()
    init_routes(app)
    init_middlewares(app)
    app.state.settings = settings

    @app.on_event("startup")
    async def on_startup():  # noqa:  WPS430
        """Действия при запуске сервера."""
        await app.container.rabbitmq().connect()

    @app.on_event("shutdown")
    async def on_shutdown():  # noqa:  WPS430
        """Действия после остановки сервера."""
        await app.container.rabbitmq().disconnect()

    return app


application = init_app()
